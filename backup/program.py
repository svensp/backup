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
        command = self.__findCommand(sys.argv[1])
        if command is None:
            return 1

        if command.usePassword():
            self.__storage.usePassword()
            
        self.__storage.load()


        return self.__runCommand(command)

    def __runCommand(self, command):
        arguments = sys.argv.copy()
        arguments.remove(arguments[0])
        arguments.remove(arguments[0])

        command.storage(self.__storage).run(arguments)

    def __findCommand(self, commandName):
        commands = self.__getCommands()
        try:
            command = commands[commandName]
            return command
        except KeyError:
            self.help()
            return None

    def help(self):
        print(sys.argv[0]+" COMMAND\n")
        print("Available Commands:")
        commands = self.__getCommands()
        for commandName in commands:
            command = commands[commandName]
            command.printDescription()

    def __getCommands(self):
        commands = {}

        CommandContainer.storageAuth().register(commands)
        CommandContainer.storageGenerateKey().register(commands)

        CommandContainer.prometheusMetrics().register(commands)

        CommandContainer.resortsList().register(commands)
        CommandContainer.resortsCreate().register(commands)
        CommandContainer.resortsRemove().register(commands)

        CommandContainer.filesCreate().register(commands)
        CommandContainer.filesPopulate().register(commands)
        CommandContainer.filesBackup().register(commands)
        CommandContainer.filesRemove().register(commands)
        CommandContainer.filesList().register(commands)
        CommandContainer.filesMount().register(commands)
        CommandContainer.filesUmount().register(commands)
        CommandContainer.filesPrune().register(commands)

        CommandContainer.mysqlCreate().register(commands)
        CommandContainer.mysqlList().register(commands)
        CommandContainer.mysqlBackup().register(commands)
        CommandContainer.mysqlRestore().register(commands)
        CommandContainer.mysqlHistory().register(commands)
        CommandContainer.mysqlPrune().register(commands)

        return commands
