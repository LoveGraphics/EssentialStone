import json
import shutil
from pathlib import Path

from endstone.plugin import Plugin


class Config:
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.root = Path.cwd() / "plugins" / "essentialstone"

        if not self.root.exists():
            self.plugin.logger.info("No base config folder found, creating one...")
            self.root.mkdir(parents=True)
            resources = Path(__file__).parent.parent / "resources"
            if resources.exists():
                shutil.copytree(resources, self.root, dirs_exist_ok=True)

    def get_configuration_file(self, filename: str = "config.json"):
        file_path = self.root / filename

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            self.plugin.logger.error(f"Failed to load {filename}: {e}")
            return False
