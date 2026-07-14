"""Read-only player information for server administration."""

import logging
import json
from pathlib import Path

from nbtlib import load

from app.classes.models.server_permissions import EnumPermissionsServer
from app.classes.web.base_api_handler import BaseApiHandler

logger = logging.getLogger(__name__)


class ApiServersServerPlayerHandler(BaseApiHandler):
    def get(self, server_id: str, player_name: str):
        auth_data = self.authenticate_user()
        if not auth_data:
            return
        if server_id not in [str(server["server_id"]) for server in auth_data[0]]:
            return self.finish_json(403, {"status": "error", "error": "NOT_AUTHORIZED"})
        mask = self.controller.server_perms.get_user_permissions_mask(
            auth_data[4]["user_id"], server_id
        )
        if (
            not auth_data[4]["superuser"]
            and EnumPermissionsServer.PLAYERS
            not in self.controller.server_perms.get_permissions(mask)
        ):
            return self.finish_json(403, {"status": "error", "error": "NOT_AUTHORIZED"})

        server = self.controller.servers.get_server_obj(server_id)
        player_file = self._find_player_file(Path(server.path), player_name)
        if player_file is None:
            return self.finish_json(404, {"status": "error", "error": "PLAYER_DATA_NOT_FOUND"})
        try:
            data = load(player_file)
            inventory = []
            for item in data.get("Inventory", []):
                inventory.append({
                    "slot": int(item.get("Slot", 0)),
                    "item": str(item.get("id", "unknown")),
                    "count": int(item.get("count", item.get("Count", 1))),
                })
            equipment = []
            equipment_slots = {"feet": 36, "legs": 37, "chest": 38, "head": 39, "offhand": 40}
            for name, slot in equipment_slots.items():
                item = data.get("equipment", {}).get(name)
                if item and item.get("id"):
                    equipment.append({
                        "slot": slot,
                        "item": str(item.get("id")),
                        "count": int(item.get("count", item.get("Count", 1))),
                    })
            position = [round(float(value), 2) for value in data.get("Pos", [])]
            result = {
                "name": player_name,
                "is_op": self._is_operator(Path(server.path), player_name),
                "health": round(float(data.get("Health", 0)), 1),
                "food": int(data.get("foodLevel", 0)),
                "position": position,
                "dimension": str(data.get("Dimension", "minecraft:overworld")),
                "inventory": inventory,
                "equipment": equipment,
                "last_death": data.get("LastDeathLocation"),
            }
            if result["last_death"]:
                result["last_death"] = {
                    "position": [int(value) for value in result["last_death"].get("pos", [])],
                    "dimension": str(result["last_death"].get("dimension", "")),
                }
            return self.finish_json(200, {"status": "ok", "data": result})
        except (OSError, TypeError, ValueError, KeyError) as why:
            logger.exception("Unable to read player data for %s", player_name)
            return self.finish_json(500, {"status": "error", "error": "PLAYER_DATA_READ_FAILED", "error_data": str(why)})

    @staticmethod
    def _find_player_file(server_path: Path, player_name: str):
        matches = []
        for root in (server_path / "world" / "players" / "data", server_path / "world" / "playerdata"):
            if not root.is_dir():
                continue
            for path in root.glob("*.dat"):
                try:
                    data = load(path)
                    known_name = str(data.get("bukkit", {}).get("lastKnownName", ""))
                    if known_name.casefold() == player_name.casefold():
                        # Offline-mode servers can have more than one UUID file
                        # for the same name. The newest file is the active one.
                        matches.append(path)
                except (OSError, ValueError, TypeError):
                    continue
        return max(matches, key=lambda path: path.stat().st_mtime, default=None)

    @staticmethod
    def _is_operator(server_path: Path, player_name: str) -> bool:
        try:
            with (server_path / "ops.json").open("r", encoding="utf-8") as ops_file:
                operators = json.load(ops_file)
            return any(
                str(operator.get("name", "")).casefold() == player_name.casefold()
                for operator in operators
            )
        except (OSError, TypeError, ValueError):
            return False
