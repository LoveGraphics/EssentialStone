import json
import functools
import uuid

from endstone import ColorFormat, Player
from endstone.command import Command, CommandSender
from endstone.event import event_handler, PlayerJoinEvent, PlayerQuitEvent, PlayerMoveEvent
from endstone.plugin import Plugin
from typing_extensions import override
from endstone_essentialstone.utils.language import Language

class EssentialStone(Plugin):
    prefix = "EssentialStone"

    api_version = "0.11"

    commands = {
        "tpa": {
            "description": "",
            "usages": ["/tpa [target: player]"],
            "permissions": ["essentialstone.command.tpa"]
        },
        "tpaccept": {
            "description": "",
            "usages": ["/tpaccept [sender: player]", "/tpaccept"],
            "permissions": ["essentialstone.command.tpaccept"]
        },
        "tpadeny": {
            "description": "",
            "usages": ["/tpadeny [sender: player]", "/tpadeny"],
            "permissions": ["essentialstone.command.tpadeny"]
        }
    }
    permissions = {
        "essentialstone.command.tpa": {
            "default": True
        },
        "essentialstone.command.tpaccept": {
            "default": True
        },
        "essentialstone.command.tpaccept": {
            "default": True
        }
    }

    @override
    def on_load(self) -> None:
        self.logger.info("Initalizing datas...")
        
        self.save_default_config()
        self.language = Language(self, self.config["language"]["lang"])

        # Save settings
        resources_path = self.data_folder / "resources"
        if not resources_path.exists(): resources_path.mkdir()
        settings_path = self.data_folder / "resources" / "settings"
        if not settings_path.exists(): settings_path.mkdir()
        self.save_resources("resources/settings/tpa.json")

        # Command's data
        tpa_settings_path = self.data_folder / "resources" / "settings" / "tpa.json"
        with open(tpa_settings_path, "r") as f: self.tpaSettings = json.load(f)
        self.tpaCooldown = {}
        self.tpaRequest = {}
        self.tpaTeleport = {}

    @override
    def on_enable(self) -> None:
        self.register_events(self)

    @override
    def on_disable(self) -> None:
        for _, data in self.tpaCooldown.items():
            if data["task"] is not None: data["task"].cancel()

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        self.tpaCooldown[str(event.player.unique_id)] = {
            "onCooldown": False,
            "task": None
        }
        self.tpaRequest[str(event.player.unique_id)] = {}

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
        playerUUID = str(event.player.unique_id)
        if self.tpaCooldown[playerUUID]["task"] is not None: self.tpaCooldown[playerUUID]["task"].cancel()
        self.tpaCooldown.pop(playerUUID)
        for _, data in self.tpaRequest[playerUUID].items(): data["task"].cancel()
        self.tpaRequest[playerUUID].clear()
        self.tpaRequest.pop(playerUUID)
    
    @event_handler
    def on_player_move(self, event: PlayerMoveEvent) -> None:
        if self.tpaSettings["can-move"]: return

        playerUUID = str(event.player.unique_id)
        if self.tpaTeleport.get(playerUUID):
            self.tpaTeleport[playerUUID]["task"].cancel()
            self.tpaTeleport.pop(playerUUID)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        match command.name:
            case "tpa":
                if len(args) == 0:
                    sender.send_message(self.language.data["tpa"]["tpa-request-args"])
                    return False
                if args[0] == sender.name:
                    sender.send_message(self.language.data["tpa"]["tpa-request-self"])
                    return False
                senderUUID = str(self.server.get_player(sender.name).unique_id)
                if self.tpaCooldown[senderUUID]["onCooldown"]:
                    sender.send_message(self.language.data["tpa"]["tpa-cooldown"].replace("{cooldown}", str(self.tpaSettings["request-cooldown"])))
                    return False
                targetUUID = self.server.get_player(args[0])
                if targetUUID is None:
                    sender.send_message(self.language.data["tpa"]["tpa-request-offline"])
                    return False
                targetUUID = str(targetUUID.unique_id)
                self.tpaCooldown[senderUUID].update({
                    "onCooldown": True,
                    "task": self.server.scheduler.run_task(self, functools.partial(self.TpaCooldownTask, senderUUID), self.tpaSettings["request-cooldown"] * 20, 20)
                })
                self.tpaRequest[targetUUID][senderUUID] = {
                    "task": self.server.scheduler.run_task(self, functools.partial(self.TpaRequestTask, senderUUID, targetUUID, args[0]), self.tpaSettings["request-expired-time"] * 20, 20)
                }
                sender.send_message(self.language.data["tpa"]["tpa-request-sent"].replace("{target_name}", args[0]))
                self.server.get_player(targetUUID).send_message(self.language.data["tpa"]["tpa-request-received"].replace("{sender_name}", sender.name))
                return True
            
            case "tpaccept":
                targetUUID = str(self.server.get_player(sender.name).unique_id)
                if len(self.tpaRequest[targetUUID]) == 0:
                    sender.send_message(self.language.data["tpa"]["tpa-request-empty"])
                    return False
                if len(args) == 0:
                    senderData = self.tpaRequest[targetUUID].popitem()
                    senderData["task"].cancel()
                    senderUUID = next(iter(senderData))
                    senderP = self.server.get_player(uuid.UUID(senderUUID))
                    if senderP is None:
                        sender.send_message(self.language.data["tpa"]["tpa-request-offline"])
                        return False
                    sender.send_message(self.language.data["tpa"]["tpa-request-accepted-target"])
                    senderP.send_message(self.language.data["tpa"]["tpa-request-accepted-sender"])
                    self.tpaTeleport[senderUUID] = {
                        "target": targetUUID,
                        "timer": self.tpaSettings["delay-before-teleport-perform"] + 1,
                        "task": self.server.scheduler.run_task(self, functools.partial(self.TpaTeleportTask, senderP, self.server.get_player(targetUUID)), 20, 20)
                    }
                    return True
                senderP = self.server.get_player(args[0])
                if senderP is None:
                    sender.send_message(self.language.data["tpa"]["tpa-request-offline"])
                    return False
                senderUUID = str(senderP.unique_id)
                if not self.tpaRequest[targetUUID].get(senderUUID):
                    sender.send_message(self.language.data["tpa"]["tpa-request-not-in-list"].replace("{sender_name}", args[0]))
                    return False
                self.tpaRequest[targetUUID][senderUUID]["task"].cancel()
                self.tpaRequest[targetUUID].pop(senderUUID)
                sender.send_message(self.language.data["tpa"]["tpa-request-accepted-target"])
                senderP.send_message(self.language.data["tpa"]["tpa-request-accepted-sender"])
                self.tpaTeleport[senderUUID] = {
                    "target": targetUUID,
                    "timer": self.tpaSettings["delay-before-teleport-perform"] + 1,
                    "task": self.server.scheduler.run_task(self, functools.partial(self.TpaTeleportTask, senderP, self.server.get_player(targetUUID)), 20, 20)
                }
                return True

            case "tpadeny":
                targetUUID = str(self.server.get_player(sender.name).unique_id)
                if len(self.tpaRequest[targetUUID]) == 0:
                    sender.send_message(self.language.data["tpa"]["tpa-request-empty"])
                    return False
                if len(args) == 0:
                    senderData = self.tpaRequest[targetUUID].popitem()
                    senderData["task"].cancel()
                    senderUUID = next(iter(senderData))
                    senderP = self.server.get_player(uuid.UUID(senderUUID))
                    sender.send_message(self.language.data["tpa"]["tpa-request-denied-target"])
                    if senderP is not None: senderP.send_message(self.language.data["tpa"]["tpa-request-denied-sender"])
                    return True
                senderP = self.server.get_player(args[0])
                if senderP is None:
                    sender.send_message(self.language.data["tpa"]["tpa-request-offline"])
                    return False
                senderUUID = str(senderP.unique_id)
                if not self.tpaRequest[targetUUID].get(senderUUID):
                    sender.send_message(self.language.data["tpa"]["tpa-request-not-in-list"].replace("{sender_name}", args[0]))
                    return False
                self.tpaRequest[targetUUID][senderUUID]["task"].cancel()
                self.tpaRequest[targetUUID].pop(senderUUID)
                sender.send_message(self.language.data["tpa"]["tpa-request-denied-target"])
                senderP.send_message(self.language.data["tpa"]["tpa-request-denied-sender"])
                return True

        return True
    
    def TpaCooldownTask(self, senderUUID: str) -> None:
        self.tpaCooldown[senderUUID]["onCooldown"] = False
        self.tpaCooldown[senderUUID]["task"].cancel()
        self.tpaCooldown[senderUUID].update({
            "task": None
        })

    def TpaRequestTask(self, senderUUID: str, targetUUID: str, targetName: str) -> None:
        sender = self.server.get_player(uuid.UUID(senderUUID))
        if sender is not None: sender.send_message(self.language.data["tpa"]["tpa-request-expired"].replace("{target_name}", targetName))
        self.tpaRequest[targetUUID][senderUUID]["task"].cancel()
        self.tpaRequest[targetUUID].pop(senderUUID)

    def TpaTeleportTask(self, sender: Player, target: Player) -> None:
        senderUUID = str(sender.unique_id)
        self.tpaTeleport[senderUUID]["timer"] -= 1
        if self.tpaTeleport[senderUUID]["timer"] <= 0:
            sender.teleport(target)
            self.tpaTeleport[senderUUID]["task"].cancel()
            return
        sender.send_popup(self.language.data["tpa"]["tpa-teleport-popup"].replace("{time}", str(self.tpaTeleport[senderUUID]["timer"])))