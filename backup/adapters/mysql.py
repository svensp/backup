import configparser
import os
import resource
import shutil
import subprocess
import tarfile
import tempfile
import pyAesCrypt

class MySQLBackup:
    def __init__(self):
        self._name = ''

    def name(self, name):
        self._name = name
        return self

    def parent(self, parent):
        self._parent = parent
        return self

    def parseInfo(self, infoContent):
        dummyHeader = '[main]\n'
        iniFile = dummyHeader+infoContent
        xtrabackupInfoContent = configparser.ConfigParser()
        xtrabackupInfoContent.read_string(iniFile)

        isFullBackup = False
        startingPoint = int(xtrabackupInfoContent['main']['innodb_from_lsn'])
        if startingPoint == 0:
            isFullBackup = True
        self._full = isFullBackup
        self._startingPoint = startingPoint

        endingPoint = int(xtrabackupInfoContent['main']['innodb_to_lsn'])
        self._endingPoint = endingPoint
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
        self._bufferSize = int(os.environ.get('MYSQL_ENC_BUFSIZE', 64 * 1024))
        self._password = os.environ.get('MYSQL_ENC_PASSWORD')


    def resort(self, resort):
        self._resort = resort
        return self

    def fullBackup(self, name, dataDir):
        dataDirAbsolute = os.path.abspath(dataDir)
        fileLimit = self.__getFileLimit()
        with tempfile.TemporaryDirectory() as tempDirectory:
            backupDirectory = tempDirectory+'/backup'
            os.mkdir(backupDirectory)
            completedProcess = subprocess.run([
                'mariabackup',
                '--backup',
                '--datadir='+dataDirAbsolute,
                '--target-dir='+backupDirectory,
                '--host='+self._mysqlHost,
                '--user='+self._mysqlUsername,
                '--password='+self._mysqlPassword,
                '--port='+self._mysqlPort,
                ])
            shutil.copy(backupDirectory+'/xtrabackup_info', tempDirectory+'/xtrabackup_info')
            tarFilePath = tempDirectory+'/backup.tar.bz2'
            tar = tarfile.open(tarFilePath, 'w:bz2')
            tar.add(backupDirectory, 'backup')
            tar.close()
            pyAesCrypt.encryptFile(tarFilePath, tarFilePath+'.enc', self._password, self._bufferSize)
            shutil.rmtree(backupDirectory)
            os.remove(tarFilePath)
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

        infoContent = self._resort.adapter('mysql').fileContent(directory+'/xtrabackup_info').decode('utf-8')
        parent = self.__parseBackupParent(directory)

        return MySQLBackup().name(backupName).parent(parent).parseInfo(infoContent)

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
