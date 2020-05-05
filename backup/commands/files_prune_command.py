from .command import Command
from datetime import datetime
import subprocess

class FilesPruneCommand(Command):
    def __init__(self):
        self._name = "files:prune"
        self._description('Mount a backup to restore files from it.')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def run(self, parameters):
        if len(parameters) < 1:
            self.printHelp()
            return 1

        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        resort.passAdapters(self)
        for repositoryNumber in  self._borg.getRepositories():
            self._borg.prune(repositoryNumber)

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME\n")
        print("Create a backup")
        print("- RESORTNAME: The resort to prune")
