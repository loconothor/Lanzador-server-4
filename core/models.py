from dataclasses import dataclass
from typing import Optional
import subprocess
import queue

@dataclass
class ServerConfig:
    id: str
    name: str
    jar: str
    path: str
    ram_min: int
    ram_max: int
    auto_restart: bool = False


class ServerRuntime:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.logs: list[str] = []
        self.log_queue = queue.Queue()

    @property
    def status(self):
        return "online" if self.running else "offline"
