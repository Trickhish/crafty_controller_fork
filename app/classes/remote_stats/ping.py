import struct
import socket
import base64
import json
import os
import re
import logging.config
import uuid
import random

from app.classes.remote_stats.raknet_ping import RaknetPing

from app.classes.shared.console import Console

logger = logging.getLogger(__name__)
MOTD_CODES = ["bold", "italic", "underlined", "strikethrough"]


class Server:
    def __init__(self, data):
        if isinstance(data, str):
            logger.error(
                "Failed to calculate stats. Expected object. "
                f"Server returned string: {data}"
            )
            return
        self.description = data.get("description")
        # print(self.description)
        if isinstance(self.description, dict):
            # cat server
            if "translate" in self.description:
                self.description = self.description["translate"]

            # waterfall / bungee
            elif "extra" in self.description:
                lines = []

                description = self.description
                if "text" in description.keys():
                    lines.append(description["text"])
                if "extra" in description.keys():
                    if isinstance(description["extra"], list):
                        for e in description["extra"]:
                            if not isinstance(e, dict):
                                lines.append(e)
                                continue
                            # Conversion format code needed only for Java Version
                            lines.append(get_code_format("reset"))
                            for item in MOTD_CODES:
                                if e.get(item, False):
                                    lines.append(get_code_format(item))
                            if "color" in e.keys():
                                lines.append(get_code_format(e["color"]))
                            # Then append the text
                            if "text" in e.keys():
                                if e["text"] == "\n":
                                    lines.append("§§")
                                else:
                                    lines.append(e["text"])

                total_text = " ".join(lines)
                self.description = total_text

            # normal MC
            else:
                self.description = self.description["text"]

        self.icon = base64.b64decode(data.get("favicon", "")[22:])
        try:
            self.players = Players(data["players"]).report()
        except KeyError:
            logger.error("Error geting player information key error")
            self.players = []
        self.version = data["version"]["name"]
        self.protocol = data["version"]["protocol"]


class Players(list):
    def __init__(self, data):
        super().__init__(Player(x) for x in data.get("sample", []))
        self.max = data.get("max", 0)
        self.online = data.get("online", 0)

    def report(self):
        players = []

        for player in self:
            players.append(str(player))

        r_data = {"online": self.online, "max": self.max, "players": players}

        return json.dumps(r_data)


class Player:
    def __init__(self, data):
        self.id = data.get("id", "")
        self.name = data.get("name", "Anonymous")

    def __str__(self):
        return self.name


def get_code_format(format_name):
    root_dir = os.path.abspath(os.path.curdir)
    format_file = os.path.join(root_dir, "app", "config", "motd_format.json")
    try:
        with open(format_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if format_name in data.keys():
            return data.get(format_name)
        logger.error(f"Format MOTD Error: format name {format_name} does not exist")
        Console.error(f"Format MOTD Error: format name {format_name} does not exist")
        return ""

    except Exception as e:
        logger.critical(f"Config File Error: Unable to read {format_file} due to {e}")
        Console.critical(f"Config File Error: Unable to read {format_file} due to {e}")

    return ""


# For the rest of requests see wiki.vg/Protocol
def ping(ip, port):
    def ping_once(proxy_header=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        def read_var_int():
            value = 0
            shift = 0
            while True:
                byte = sock.recv(1)
                if not byte:
                    raise ValueError("connection closed while reading varint")
                byte = byte[0]
                value |= (byte & 0x7F) << shift
                if not byte & 0x80:
                    return value
                shift += 7
                if shift > 35:
                    raise ValueError("var_int too big")

        try:
            sock.connect((ip, port))
            host = ip.encode("utf-8")
            data = b"\x00\x04"  # packet ID and legacy-compatible protocol
            data += struct.pack(">b", len(host)) + host
            data += struct.pack(">H", port)
            data += b"\x01"  # next state: status
            handshake = struct.pack(">b", len(data)) + data
            status_ping = b"\x01\x00"
            sock.sendall((proxy_header or b"") + handshake + status_ping)

            packet_length = read_var_int()
            if packet_length < 10:
                return False
            sock.recv(1)  # packet type, 0 for pings
            data_length = read_var_int()
            data = b""
            while len(data) != data_length:
                chunk = sock.recv(data_length - len(data))
                if not chunk:
                    return False
                data += chunk
            logger.debug("Server reports this data on ping: %s", data)
            try:
                return Server(json.loads(data))
            except (KeyError, json.decoder.JSONDecodeError):
                return {}
        except (OSError, ValueError, json.decoder.JSONDecodeError):
            return False
        finally:
            sock.close()

    result = ping_once()
    if result:
        return result

    # Paper servers configured for HAProxy require this header before the
    # Minecraft handshake. Retry with a local IPv4 PROXY protocol header so
    # Crafty can monitor those servers without affecting normal servers.
    proxy_header = f"PROXY TCP4 127.0.0.1 {ip} 25565 {port}\r\n".encode("ascii")
    return ping_once(proxy_header)


# For the rest of requests see wiki.vg/Protocol
def ping_raknet(ip, port):
    rand = random.Random()
    try:
        # pylint: disable=consider-using-f-string
        rand.seed("".join(re.findall("..", "%012x" % uuid.getnode())))
        client_guid = uuid.UUID(int=rand.getrandbits(32)).int
    except:
        client_guid = 0
    try:
        brp = RaknetPing(ip, port, client_guid)
        return brp.ping()
    except:
        logger.exception("Unable to get RakNet stats")
