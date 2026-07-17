from endstone.plugin import Plugin
from typing_extensions import override

from endstone_essentialstone.utils.config import Config


class EssentialStone(Plugin):
   prefix = "EssentialStone"

   api_version = "0.11"

   @override
   def on_load(self) -> None:
      self.logger.info("Initalizing datas...")
      self.pluginConfig = Config(self)
      
   @override
   def on_enable(self) -> None:
       pass
