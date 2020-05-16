from .command import Command
from datetime import datetime
import subprocess

class FilesListCommand(Command):
    def __init__(self):
        self._name = "files:list"
        self._description('List all availables file backups')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def run(self, parameters):
        if len(parameters) < 1:
            self.printHelp()
            return 1

        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        repositoryNumber = "1"
        if len(parameters) >= 2:
            repositoryNumber = parameters[1]

        resort.passAdapters(self)
        for backup in self._borg.list(repositoryNumber):
            backup.print()


    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME TARGET\n")
        print("Create a backup")
        print("- RESORTNAME: The resort in which to make file backup available")
        print("- The directory to backup")
