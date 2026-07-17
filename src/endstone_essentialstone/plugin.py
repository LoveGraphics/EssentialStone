import json

from endstone.plugin import Plugin, PluginCommand
from typing_extensions import override

<<<<<<< HEAD
from endstone_essentialstone.Command import *
=======
from endstone_essentialstone.utils.config import Config

>>>>>>> e6c91a9fb3c486f764d628af3c06d971fade0d63

class EssentialStone(Plugin):
    prefix = "EssentialStone"

    api_version = "0.11"

<<<<<<< HEAD
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
=======
   @override
   def on_load(self) -> None:
      self.logger.info("Initalizing datas...")
      self.pluginConfig = Config(self)
      
   @override
   def on_enable(self) -> None:
       pass
>>>>>>> e6c91a9fb3c486f764d628af3c06d971fade0d63
