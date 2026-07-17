from abc import ABC, abstractmethod

from endstone.command import Command, CommandSender
from endstone.plugin import Plugin

class BaseCommand(ABC):

    def __init__(self, plugin: Plugin, commandName: str, description: str, usages: list[str], permissions: list[str]):
        self.plugin = plugin
        self.commandName = commandName
        self.description = description
        self.usages = usages
        self.permissions = permissions

    @abstractmethod
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        pass

class TpaCommand(BaseCommand):

    def __init__(self, plugin: Plugin, commandName: str, description: str, usages: list[str], permissions: list[str]):
        super().__init__(plugin, commandName, description, usages, permissions)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        pass