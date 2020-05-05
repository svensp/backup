import configparser
import tempfile
import os
import os.path
import subprocess
import resource

class MySQLBackup:
    def __init__(self):
        self._name = ''

    def name(self, name):
        self._name = name
        return self

    def parent(self, parent):
        self._parent = parent
        return self

    def full(self, full):
        self._full = full
        return self

    def print(self):
        typeName = 'INCREMENTAL'
        if self._full:
            typeName = 'FULL'
            
        print(self._name + ' - ' + typeName + ' - '+ self._parent)

class MySQL:
    def __init__(self):
        self._mysqlHost = os.environ.get('MYSQL_HOST', 'mysql')
        self._mysqlPort = os.environ.get('MYSQL_PORT', '3306')
        self._mysqlUsername = os.environ.get('MYSQL_USERNAME', 'backup')
        self._mysqlPassword = os.environ.get('MYSQL_PASSWORD')
        self._backupCommand = os.environ.get('MYSQL_COMMAND', 'mariabackup')

    def resort(self, resort):
        self._resort = resort
        return self

    def fullBackup(self, name, dataDir):
        dataDirAbsolute = os.path.abspath(dataDir)
        fileLimit = self.__getFileLimit()
        with tempfile.TemporaryDirectory() as tempDirectory:
            completedProcess = subprocess.run([
                'mariabackup',
                '--backup',
                '--datadir='+dataDirAbsolute,
                '--target-dir='+tempDirectory,
                '--host='+self._mysqlHost,
                '--user='+self._mysqlUsername,
                '--password='+self._mysqlPassword,
                '--port='+self._mysqlPort,
                ])
            self._resort.adapter('mysql').upload(tempDirectory, name)


        return self

    def __getFileLimit(self):
        limits = resource.getrlimit(resource.RLIMIT_NOFILE)
        return limits[1]

    def list(self):
        backups = []
        for directory in self._resort.adapter('mysql').listFolders(): 
            backup = self.__parseBackup(directory)
            backups.append(backup)
        return backups

    def __parseBackup(self, directory):
        backupName = os.path.basename(directory)

        dummyHeader = '[main]\n'
        infoContent = self._resort.adapter('mysql').fileContent(directory+'/xtrabackup_info').decode('utf-8')
        iniFile = dummyHeader+infoContent
        xtrabackupInfoContent = configparser.ConfigParser()
        xtrabackupInfoContent.read_string(iniFile)

        isFullBackup = False
        if int(xtrabackupInfoContent['main']['innodb_from_lsn']) == 0:
            isFullBackup = True
            

        parent = self.__parseBackupParent(directory)
        return MySQLBackup().name(backupName).full(isFullBackup).parent(parent)

    def __parseBackupParent(self, directory):

        try:
            backupHistory = self._resort.adapter('mysql').fileContent(directory+'/backup_history.txt').decode('utf-8')
        except FileNotFoundError:
            return ""
        backupHistoryLines = backupHistory.split('\n')
        lastBackupLineIndex = len(backupHistoryLines) - 1
        lastBackupLine = backupHistoryLines[lastBackupLineIndex]
        if not lastBackupLine:
            lastBackupLineIndex = len(backupHistoryLines) - 2
            lastBackupLine = backupHistoryLines[lastBackupLineIndex]

        parent = lastBackupLine
        return parent
