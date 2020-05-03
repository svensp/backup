from .command import Command
from datetime import datetime
import subprocess

class FilesMountCommand(Command):
    def __init__(self):
        self._name = "files:mount"
        self._description('Mount a backup to restore files from it.')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def run(self, parameters):
        if len(parameters) < 3:
            self.printHelp()
            return 1

        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        name = parameters[1]
        target = parameters[2]

        repositoryNumber = 1
        if len(parameters) >= 4:
            repositoryNumber = parameters[3]
            
        resort.passAdapters(self)
        self._borg.mount(name, target, repositoryNumber)

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME BACKUP TARGET [REPOSITORY]\n")
        print("Create a backup")
        print("- RESORTNAME: The resort in which to make file backup available")
        print("- BACKUP: The name of the backup. Check available bakcups with files:list")
        print("- TARGET: Directory to mount the backup to")
        print("- REPOSITORY: From which repository to mount. Defaults to 1")
