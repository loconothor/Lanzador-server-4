from core.server_manager import ServerManager

class Api:
    def __init__(self):
        self.manager = ServerManager()

    def get_servers(self):
        return self.manager.list_servers()

    def start_server(self, server_id):
        self.manager.start_server(server_id)
        return {"ok": True}

    def stop_server(self, server_id):
        self.manager.stop_server(server_id)
        return {"ok": True}

    def get_logs(self, server_id):
        return self.manager.get_logs(server_id)

    def create_server(self, data):
        cfg = self.manager.create_server(data)
        return vars(cfg)
