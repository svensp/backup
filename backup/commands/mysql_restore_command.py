import argparse
from .command import Command
from datetime import datetime

class MysqlRestoreCommand(Command):
    def __init__(self):
        self._name = "mysql:restore"
        self._description( 'restore a mysql backup')

    def setMySQL(self, mysql):
        self._mysql = mysql
        return self

    def run(self, parameters):
        args = self.__parseArgs(parameters)

        resortName = args.resortName
        resort = self._storage.findResort(resortName)
        resort.passAdapters(self)

        backupName = args.backupName
        dataDir = args.dataDir
        port = 8080
        if args.port:
            port = int(args.port[0])

        print("Restoring Backup "+backupName+" to "+dataDir)
        self._mysql.setOutput(self)
        self._mysql.restore(backupName, dataDir, port)
        print("Restored Backup "+backupName)

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser()
        parser.add_argument('resortName', help='The resort in which to create the backup')
        parser.add_argument('backupName', help='The name of the backup to restore')
        parser.add_argument('dataDir', help='The directory where to restore the backup')
        parser.add_argument('--port', nargs=1, help='The port of the pma in the created docker-compose.yml', type=int)
        return parser.parse_args(parameters)
