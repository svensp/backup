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
        if len(parameters) < 3:
            self.printHelp()
            return 1


        resortName = parameters[0]
        resort = self._storage.findResort(resortName)
        resort.passAdapters(self)

        name = parameters[1]
        dataDir = parameters[2]

        print("Searching for backup "+name+" to "+dataDir)
        backup = self._mysql.find(name)

        print("Restoring Backup "+name+" to "+dataDir)
        backup.restore(dataDir)
        print("Restored Backup "+name)

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME BACKUPNAME DATADIR\n")
        print("Make sure file backup is available in a resort")
        print("- RESORTNAME: The resort in which to create the backup")
        print("- BACKUPNAME: The backup to restore")
        print("- DATADIR: The directory in which to restore the backup")
