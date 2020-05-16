import argparse
import os
from .command import Command
from datetime import datetime

class NotEmptyError(Exception):
    pass

class Directory():
    def __init__(self, path):
        self._path = path

    def assertEmpty(self):
        self.__assertEmpty(self._path)

    def __assertEmpty(self, path):
        for entry in os.listdir(path):
            entryPath = '/'.join([
                path,
                entry,
                ])
            if not os.path.isdir(entryPath):
                raise NotEmptyError(self._path+" is not empty: "+entryPath)
            self.__assertEmpty(entryPath)

class FilesPopulateCommand(Command):
    def __init__(self):
        self._name = "files:populate"
        self._description('''Restore the latest backup if the target directory is empty.
Empty meaning it contains no files but may contain directories''')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def run(self, parameters):
        self.__parseArgs(parameters)

        resortName = self._args.resortName
        resort = self._storage.findResort(resortName)

        target = self._args.target

        repositoryNumber = self._args.repository
            
        targetDirectory = Directory(target)
        targetDirectory.assertEmpty()
        resort.passAdapters(self)
        self._borg.restore('latest', target, repositoryNumber)

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser(description='''Restore the latest backup if the target directory is empty.
Empty meaning it contains no files but may contain directories''')
        parser.add_argument(
                'resortName',
                help='Resort from which the backup is taken'
                )
        parser.add_argument(
                'target',
                help='The directory into which to restore'
                )
        parser.add_argument(
                '--repository',
                '-r',
                help='The copy from which to load the backup',
                default=1,
                )
        self._args = parser.parse_args(parameters)
