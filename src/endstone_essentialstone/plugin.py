import time
import uuid

from endstone.command import Command, CommandSender
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
            "usages": ["/tpaccept [sender: player]"],
            "permissions": ["essentialstone.command.tpaccept"]
        }
    }
    permissions = {
        "essentialstone.command.tpa": {
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

        # Command's data
        self.tpaSettings = {}
        self.tpaCooldown = {}
        self.tpaRequest = {}

    @override
    def on_enable(self) -> None:
        self.server.scheduler.run_task(self, self.TpaCooldownCleaner, 0, self.tpaSettings["request-cooldown"] * 20)
        self.server.scheduler.run_task(self, self.TpaRequestCleaner, 0, self.tpaSettings["request-expired-time"] * 20)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        match command.name:
            case "tpa":
                if args[0] == sender.name:
                    sender.send_message(self.language.data["tpa"]["tpa-request-self"])
                    return False
                currentTime = time.time()
                requestCooldown = self.tpaSettings["request-cooldown"]
                senderUUID = str(self.server.get_player(sender.name).unique_id)
                if not self.tpaCooldown[senderUUID]: self.tpaCooldown[senderUUID] = currentTime - requestCooldown
                if currentTime - self.tpaCooldown[senderUUID] < requestCooldown:
                    sender.send_message(self.language.data["tpa"]["tpa-cooldown"].replace("{cooldown}", str(requestCooldown)))
                    return False
                targetUUID = str(self.server.get_player(args[0]).unique_id)
                self.tpaCooldown[senderUUID] = currentTime
                if not self.tpaRequest[targetUUID]: self.tpaRequest[targetUUID] = {}
                self.tpaRequest[targetUUID][senderUUID] = currentTime
                sender.send_message(self.language.data["tpa"]["tpa-request-sent"].replace("{target_name}", args[0]))
                self.server.get_player(args[0]).send_message(self.language.data["tpa"]["tpa-request-received"].replace("{sender_name}", sender.name))
                
                return True
            
            case "tpaccept":
                if len(args) == 0:
                    senderUUID = str(self.server.get_player(sender.name).unique_id)
                    if not self.tpaRequest.get(senderUUID):
                        sender.send_message(self.language.data["tpa"]["tpa-request-empty"])
                        return False
                    if len(self.tpaRequest[senderUUID]) == 0:
                        sender.send_message(self.language.data["tpa"]["tpa-request-empty"])
                        return False
                    senderCUUID = next(iter(self.tpaRequest[senderUUID].popitem()))
                    if len(self.tpaRequest[senderUUID]) == 0: self.tpaRequest.pop(senderUUID)
                    senderCPlayer = self.server.get_player(uuid.UUID(senderCUUID))
                    senderCPlayer.teleport(self.server.get_player(sender.name))
                    sender.send_message(self.language.data["tpa"]["tpa-request-accepted_receiver"])
                    senderCPlayer.send_message(self.language.data["tpa"]["tpa-request-accepted_sender"])

        return True
    
    def TpaCooldownCleaner(self) -> None:
        currentTime = time.time()
        requestCooldown = self.tpaSettings["request-cooldown"]
        for uuid, cooldown in self.tpaCooldown.items():
            if currentTime - cooldown >= requestCooldown: self.tpaCooldown.pop(uuid)

    def TpaRequestCleaner(self) -> None:
        currentTime = time.time()
        expiredTime = self.tpaSettings["request-expired-time"]
        for targetUUID, requests in self.tpaRequest.items():
            for senderUUID, expiredTime_ in requests.items():
                if currentTime - expiredTime_ >= expiredTime:
                    requests.pop(senderUUID)
                    if len(requests) == 0: self.tpaRequest.pop(targetUUID)