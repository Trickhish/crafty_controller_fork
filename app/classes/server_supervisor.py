"""Central daemon that launches and routes commands to per-server workers."""

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


class Supervisor:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.workers = {}

    @staticmethod
    def request(socket_path, payload):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(3)
            connection.connect(socket_path)
            connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            return json.loads(connection.makefile("rb").readline())

    def start_worker(self, request):
        server_id = request["server_id"]
        worker_socket = request["worker_socket"]
        try:
            status = self.request(worker_socket, {"action": "status"})
            if status.get("running"):
                return status
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        Path(worker_socket).unlink(missing_ok=True)
        command = [
            sys.executable,
            "-m",
            "app.classes.server_worker",
            "--socket",
            worker_socket,
            "--cwd",
            request["cwd"],
            "--log",
            request["log_path"],
            *request["command"],
        ]
        subprocess.Popen(command, cwd=request["project_root"], start_new_session=True)
        for _ in range(50):
            time.sleep(0.1)
            try:
                status = self.request(worker_socket, {"action": "status"})
                if status.get("running"):
                    self.workers[server_id] = worker_socket
                    return status
            except (OSError, ValueError, json.JSONDecodeError):
                continue
        return {"ok": False, "error": "worker did not start"}

    def handle(self, request):
        action = request.get("action")
        if action == "start":
            return self.start_worker(request)
        worker_socket = self.workers.get(request.get("server_id"), request.get("worker_socket"))
        if not worker_socket:
            return {"ok": False, "error": "server worker is not registered"}
        try:
            return self.request(worker_socket, request)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return {"ok": False, "error": str(error)}

    def serve(self):
        path = Path(self.socket_path)
        path.unlink(missing_ok=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.socket_path)
        os.chmod(self.socket_path, 0o660)
        server.listen(16)
        while True:
            connection, _ = server.accept()
            with connection:
                try:
                    request = json.loads(connection.makefile("rb").readline())
                    response = self.handle(request)
                except (OSError, json.JSONDecodeError, KeyError) as error:
                    response = {"ok": False, "error": str(error)}
                connection.sendall((json.dumps(response) + "\n").encode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", default="/var/opt/minecraft/crafty-fork-data/supervisor.sock")
    args = parser.parse_args()
    Supervisor(args.socket).serve()


if __name__ == "__main__":
    main()
