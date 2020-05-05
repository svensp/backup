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
        if len(parameters) < 2:
            self.printHelp()
            return 1


        resortName = parameters[0]
        resort = self._storage.findResort(resortName)
        resort.passAdapters(self)

        name = datetime.now().strftime('%Y-%m-%d_%H-%M')
        dataDir = parameters[1]

        print("Creating Backup "+name)
        self._mysql.fullBackup(name, dataDir)
        print("Created Backup "+name)

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME DATADIR\n")
        print("Make sure file backup is available in a resort")
        print("- RESORTNAME: The resort in which to create the backup")
        print("- DATADIR: The data directory of the mariadb server")
