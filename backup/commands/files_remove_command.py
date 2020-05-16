import argparse
from .command import Command
from datetime import datetime

class FilesRemoveCommand(Command):
    def __init__(self):
        self._name = "files:remove"
        self._description('Remove a file backup')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def run(self, parameters):
        self.__parseArgs(parameters)

        resortName = self._args.resortName
        resort = self._storage.findResort(resortName)

        name = self._args.backupName
        resort.passAdapters(self)
        for repo in self._borg.getRepositories():
            self._borg.remove(name, repo)

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser(description='Remove a file backup')
        parser.add_argument('resortName', help='Resort')
        parser.add_argument('backupName', help='The name of the backup to remove')
        self._args = parser.parse_args(parameters)
