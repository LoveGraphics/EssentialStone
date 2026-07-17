import json

from endstone.plugin import Plugin

class Language:

    def __init__(self, plugin: Plugin, language: str):
        self.plugin = plugin
        self.language = language

        resources_path = self.plugin.data_folder / "resources"
        if not resources_path.exists(): resources_path.mkdir()
        language_path = self.plugin.data_folder / "resources" / "languages"
        if not language_path.exists(): language_path.mkdir()

        self.LoadLanguageData()

    def LoadLanguageData(self) -> bool:
        self.plugin.save_resources("resources/languages/" + self.language + ".json")

        language_data_path = self.plugin.data_folder / "resources" / "languages" / (self.language + ".json")
        try:
            with open(language_data_path, "r") as f: self.data = json.load(f)
        except:
            self.plugin.plugin_loader.disable_plugin(self.plugin)
