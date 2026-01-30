import os
import json
import threading
import subprocess
from uuid import uuid4
from .models import ServerConfig, ServerRuntime

CREATE_NO_WINDOW = 0x08000000


class ServerManager:
    def __init__(self, data_file="servers.json"):
        self.data_file = data_file
        self.servers: dict[str, ServerRuntime] = {}
        self.load()

    # ===================== DATA =====================
    def load(self):
        if not os.path.exists(self.data_file):
            return

        with open(self.data_file, "r", encoding="utf-8") as f:
            for data in json.load(f):
                cfg = ServerConfig(**data)
                self.servers[cfg.id] = ServerRuntime(cfg)

    def save(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(
                [vars(s.config) for s in self.servers.values()],
                f,
                indent=4
            )

    # ===================== CRUD =====================
    def create_server(self, data: dict):
        cfg = ServerConfig(
            id=str(uuid4()),
            name=data["name"],
            jar=data["jar"],
            path=data["path"],
            ram_min=data["ram_min"],
            ram_max=data["ram_max"],
            auto_restart=data.get("auto_restart", False)
        )
        self.servers[cfg.id] = ServerRuntime(cfg)
        self.save()
        return cfg

    def delete_server(self, server_id: str):
        srv = self.servers.get(server_id)
        if srv and srv.running:
            self.stop_server(server_id)
        self.servers.pop(server_id, None)
        self.save()

    # ===================== PROCESS =====================
    def start_server(self, server_id: str):
        srv = self.servers.get(server_id)
        if not srv or srv.running:
            return

        cfg = srv.config
        jar_path = os.path.join(cfg.path, cfg.jar)
        if not os.path.exists(jar_path):
            raise FileNotFoundError("Jar no encontrado")

        cmd = [
            "java",
            f"-Xms{cfg.ram_min}G",
            f"-Xmx{cfg.ram_max}G",
            "-jar",
            cfg.jar,
            "nogui"
        ]

        def run():
            srv.running = True
            srv.process = subprocess.Popen(
                cmd,
                cwd=cfg.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=CREATE_NO_WINDOW
            )

            for line in srv.process.stdout:
                line = line.rstrip()
                srv.logs.append(line)
                srv.log_queue.put(line)

            srv.running = False

        threading.Thread(target=run, daemon=True).start()

    def stop_server(self, server_id: str):
        srv = self.servers.get(server_id)
        if srv and srv.process:
            try:
                srv.process.stdin.write("stop\n")
                srv.process.stdin.flush()
            except:
                pass

    # ===================== LOGS =====================
    def get_logs(self, server_id: str):
        srv = self.servers.get(server_id)
        if not srv:
            return []

        logs = []
        while not srv.log_queue.empty():
            logs.append(srv.log_queue.get())

        return logs

    # ===================== INFO =====================
    def list_servers(self):
        return [
            {
                "id": s.config.id,
                "name": s.config.name,
                "status": s.status,
                "ram_min": s.config.ram_min,
                "ram_max": s.config.ram_max,
            }
            for s in self.servers.values()
        ]
