from endstone.plugin import Plugin
from typing_extensions import override

class EssentialStone(Plugin):
   prefix = "EssentialStone"

   api_version = "0.11"

   @override
   def on_load(self) -> None:
      self.logger.info("Initalizing datas...")

   @override
   def on_enable(self) -> None:
      self.save_default_config()
