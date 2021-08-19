from .command import Command
from datetime import datetime
import subprocess

class MysqlListCommand(Command):
    def __init__(self):
        self._name = "mysql:list"
        self._description('List all available mysql backups')

    def setMySQL(self, mysql):
        self._mysql = mysql
        return self

    def run(self, parameters):
        if len(parameters) < 1:
            self.printHelp()
            return 1

        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        resort.passAdapters(self)
        for backup in self._mysql.list():
            if backup.isFull():
                backup.printRecursive()

        print('Special names:')
        specialNameBackups = self._mysql.getSpecialBackups()
        for specialName in specialNameBackups:
            specialNameBackups[specialName].print(prefix=specialName+' ')

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME\n")
        print("List available mysql backups")
        print("- RESORTNAME: The resort in which to make file backup available")
