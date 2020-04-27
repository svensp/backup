import sys
import os
from .config import Config
from .storage import StorageContainer
from .commands import CommandContainer

class Program:

    def setUp(self):
        self.__config = Config()
        self.__config.parse(os.environ)
        self.__storage = StorageContainer.hetzner()

    def run(self):
        if len(sys.argv) <= 1:
            self.help()
            return 0

        self.setUp()
        self.__storage.load()


        return self.__runCommand(sys.argv[1])

    def __runCommand(self, commandName):
        commands = self.__getCommands()
        try:
            command = commands[commandName]
        except KeyError:
            self.help()
            return 0

        command.storage(self.__storage).run()

    def help(self):
        print(sys.argv[0]+" COMMAND\n")
        print("Available Commands:")
        commands = self.__getCommands()
        for commandName in commands:
            command = commands[commandName]
            command.printDescription()

    def __getCommands(self):
        commands = {
                "resorts": CommandContainer.resorts()
        }
        return commands
