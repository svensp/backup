from .command import Command
from datetime import datetime
import subprocess

class FilesUmountCommand(Command):
    def __init__(self):
        self._name = "files:umount"
        self._description('Umount a backup to restore files from it.')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def run(self, parameters):
        if len(parameters) < 1:
            self.printHelp()
            return 1

        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        target = parameters[1]

        resort.passAdapters(self)
        self._borg.umount(target)

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME MOUNTPATH\n")
        print("Unmount a previously monuted backup")
        print("- RESORTNAME: The resort from which the backup was mounted")
        print("- MOUNTPATH: The path to which the backup was mounted")
