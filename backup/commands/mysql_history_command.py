import argparse
from .command import Command
from datetime import datetime

class MysqlHistoryCommand(Command):
    def __init__(self):
        self._name = "mysql:history"
        self._description('List the history of a given backup')

    def setMySQL(self, mysql):
        self._mysql = mysql
        return self

    def run(self, parameters):
        args = self.__parseArgs(parameters)

        resortName = args.resortName
        resort = self._storage.findResort(resortName)

        resort.passAdapters(self)
        backupName = args.backupName
        backup = self._mysql.find(backupName)
        fullBackup, history = backup.getHistory()
        print('Full Backup: '+fullBackup._name)
        for backup in history:
            print(backup._name)

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser()
        parser.add_argument('resortName', help='The resort in which to create the backup')
        parser.add_argument('backupName', help='The backup for which the history should be listed')
        return parser.parse_args(parameters)
