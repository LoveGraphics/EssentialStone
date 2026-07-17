import json

from endstone.plugin import Plugin, PluginCommand
from typing_extensions import override

from endstone_essentialstone.Command import *

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
        self.pluginConfig = Config(self)


    @override
    def on_enable(self) -> None:
        pass