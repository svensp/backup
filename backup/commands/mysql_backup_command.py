import argparse
import sys
from .command import Command
from datetime import datetime

class MysqlBackupCommand(Command):
    def __init__(self):
        self._name = "mysql:backup"
        self._description( 'Perform a mysql backup')

    def setMySQL(self, mysql):
        self._mysql = mysql
        return self

    def run(self, parameters):
        args = self.__parseArgs(parameters)

        resortName = args.resortName
        resort = self._storage.findResort(resortName)
        resort.passAdapters(self)

        name = datetime.now().strftime('%Y-%m-%d_%H-%M')
        dataDir = args.dataDir

        tags = args.tags
        if not tags:
            tags = []
            

        if args.parent:
            tags.append('incremental')
            parentName = args.parent[0]
            print("Creating incremental Backup "+name+" based on "+parentName)
            self._mysql.tags(tags).incrementalBackup(name, parentName)
            print("Created incremental Backup "+name+" based on "+parentName)
            return 0

        tags.append('full')
        print("Creating complete Backup "+name)
        self._mysql.tags(tags).fullBackup(name)
        print("Created complete Backup "+name)
        return 0

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser()
        parser.add_argument('resortName', help='The resort in which to create the backup')
        parser.add_argument('--parent', nargs=1, help='Create an incremental backup based on the given parent')
        parser.add_argument('--tags', nargs='*', help='Tags')
        return parser.parse_args(parameters)
