from endstone.plugin import Plugin
from typing_extensions import override
from endstone_essentialstone.utils.language import Language

class EssentialStone(Plugin):
    prefix = "EssentialStone"

    api_version = "0.11"

    commands = {
        "tpa": {
            "description": "",
            "usages": ["/tpa"],
            "permissions": ["essentialstone.command.tpa"]
        }
    }
    permissions = {
        "essentialstone.command.tpa": {
            "default": True
        }
    }

    @override
    def on_load(self) -> None:
        self.logger.info("Initalizing datas...")
        
        self.save_default_config()
        self.language = Language(self, self.config["language"]["lang"])

    @override
    def on_enable(self) -> None:
        pass