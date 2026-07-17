import json

from endstone.plugin import Plugin
from typing_extensions import override

class EssentialStone(Plugin):
   prefix = "EssentialStone"

   api_version = "0.11"

   @override
   def on_load(self) -> None:
      self.logger.info("Load languages...")
      self.save_resources("eng.json")
      language_data_path = self.data_folder / (self.config.get("language") + ".json")
      try:
          with open(language_data_path, "r") as f:
              language = json.load(f)
              self.logger.info("Current language: " + self.config.get("language"))
      except:
          self.logger.info("Invalid language in config file, disabling...")
          self.server.plugin_manager.disable_plugin(self)


   @override
   def on_enable(self) -> None:
      self.save_default_config()
