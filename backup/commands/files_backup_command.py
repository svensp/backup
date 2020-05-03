from .command import Command
from datetime import datetime
import subprocess

class FilesBackupCommand(Command):
    def __init__(self):
        self._name = "files:backup"
        self._description('Create a file backup')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def run(self, parameters):
        if len(parameters) < 2:
            self.printHelp()
            return 1

        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        target = parameters[1]
        name = datetime.now().strftime('%Y-%m-%d_%H-%M')
        resort.passAdapters(self)
        for repo in self._borg.getRepositories():
            self._borg.backup(name, target, repo)

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME TARGET\n")
        print("Create a backup")
        print("- RESORTNAME: The resort in which to make file backup available")
        print("- The directory to backup")
