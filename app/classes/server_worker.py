"""Small persistent process owner used to decouple Minecraft from Crafty."""

import argparse
import json
import os
import shlex
import signal
import socket
import subprocess
import sys
from pathlib import Path


def send_response(connection, payload):
    connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))


def run_worker(socket_path, cwd, command, log_path):
    path = Path(socket_path)
    path.unlink(missing_ok=True)
    Path(cwd).mkdir(parents=True, exist_ok=True)
    log_file = open(log_path, "ab", buffering=0)  # pylint: disable=consider-using-with
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdin=subprocess.PIPE,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
    )

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    os.chmod(socket_path, 0o660)
    server.listen(5)

    def close_worker(_signum=None, _frame=None):
        server.close()
        log_file.close()
        path.unlink(missing_ok=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, close_worker)
    signal.signal(signal.SIGINT, close_worker)
    try:
        while process.poll() is None:
            try:
                server.settimeout(1)
                connection, _ = server.accept()
            except socket.timeout:
                continue
            with connection:
                try:
                    request = json.loads(connection.makefile("rb").readline())
                    action = request.get("action")
                    if action == "status":
                        send_response(connection, {"running": process.poll() is None, "pid": process.pid})
                    elif action == "write":
                        process.stdin.write(request.get("command", "").encode("utf-8"))
                        process.stdin.flush()
                        send_response(connection, {"ok": True})
                    elif action == "terminate":
                        process.terminate()
                        send_response(connection, {"ok": True})
                    elif action == "kill":
                        process.kill()
                        send_response(connection, {"ok": True})
                    else:
                        send_response(connection, {"ok": False, "error": "unknown action"})
                except (BrokenPipeError, json.JSONDecodeError, OSError) as error:
                    send_response(connection, {"ok": False, "error": str(error)})
    finally:
        close_worker()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    run_worker(args.socket, args.cwd, args.command, args.log)


if __name__ == "__main__":
    main()
