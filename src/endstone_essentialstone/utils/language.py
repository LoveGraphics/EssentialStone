from endstone.plugin import Plugin

from endstone_essentialstone.utils.config import Config


class Language:
    def __init__(self, plugin: Plugin, base_language):
        self.plugin = plugin
        self.base_language = base_language
        self.config = Config(plugin)

    def is_available(self):
        return self.config.get_configuration_file("languages/" + self.base_language)
