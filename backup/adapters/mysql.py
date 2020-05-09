import configparser
import os
import resource
import shutil
import subprocess
import tarfile
import tempfile
import pyAesCrypt

class BackupNotFoundException(Exception):
    pass

class MySQLBackupMeta:
    def __init__(self):
        self.byEndingPoint = {}
        self.byStartingPoint = {}

    def addByEndingPoint(self, endingPoint,backup):
        try:
            self.byEndingPoint[endingPoint].append(backup)
        except KeyError:
            self.byEndingPoint[endingPoint] = [ backup ]
        return self

    def addByStartingPoint(self, startingPoint,backup):
        try:
            self.byStartingPoint[startingPoint].append(backup)
        except KeyError:
            self.byStartingPoint[startingPoint] = [ backup ]
        return self

    def parent(self, childStartingPoint):
        try:
            return self.byEndingPoint[childStartingPoint][0]
        except KeyError:
            return None

    def children(self, parentEndingPoint):
        try:
            return self.byStartingPoint[parentEndingPoint]
        except KeyError:
            return []

class MySQLBackup:
    def __init__(self):
        self._name = ''

    def mysql(self, mysql):
        self._mysql = mysql
        return self

    def name(self, name):
        self._name = name
        return self

    def meta(self, meta):
        self._meta = meta
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

        self._meta.addByEndingPoint(endingPoint, self)
        self._meta.addByStartingPoint(startingPoint, self)

        return self

    def isNamed(self, name):
        return self._name == name

    def isFull(self):
        return self._full

    def print(self, indent = 0):
        print( (' ' * indent) + self._name)

        for child in self.getChildren():
            child.print(indent + 2)
                

    def getParent(self):
        if self._full:
            return None
        return self._meta.parent(self._startingPoint)

    def getChildren(self):
        return self._meta.children(self._endingPoint)

    def inject(self, backupList):
        backupList.append(self)
        return self

class MySQL:
    def __init__(self):
        self._mysqlHost = os.environ.get('MYSQL_HOST', 'mysql')
        self._mysqlPort = os.environ.get('MYSQL_PORT', '3306')
        self._mysqlUsername = os.environ.get('MYSQL_USERNAME', 'backup')
        self._mysqlPassword = os.environ.get('MYSQL_PASSWORD')
        self._backupCommand = os.environ.get('MYSQL_COMMAND', 'mariabackup')
        self._bufferSize = int(os.environ.get('MYSQL_ENC_BUFSIZE', 64 * 1024))
        self._password = os.environ.get('MYSQL_ENC_PASSWORD')
        self._assetBase = os.path.dirname(os.path.realpath(__file__))+'/assets'


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
            pyAesCrypt.encryptFile(tarFilePath, tarFilePath+'.aes', self._password, self._bufferSize)
            shutil.rmtree(backupDirectory)
            os.remove(tarFilePath)
            self._resort.adapter('mysql').upload(tempDirectory, name)
        return self

    def find(self, name):
        availableBackups = self.list()
        for backup in availableBackups:
            if backup.isNamed(name):
                return backup
        raise BackupNotFoundException()

    def restore(self, name, dataDir):
        dataDirAbsolute = os.path.abspath(dataDir)
        backup = self.__parseBackup(name)
        self._resort.adapter('mysql').download(name, dataDirAbsolute)
        tarFilePath = dataDirAbsolute+'/backup.tar.bz2'
        pyAesCrypt.decryptFile(tarFilePath+'.aes', tarFilePath, self._password, self._bufferSize)
        tar = tarfile.open(tarFilePath, 'r:bz2')
        tar.extractall(dataDir)
        completedProcess = subprocess.run([
            'mariabackup',
            '--prepare',
            '--target-dir='+dataDirAbsolute+'/backup',
            ])
        shutil.copy(self._assetBase+'/docker-compose.yml',
                dataDirAbsolute+'/backup/docker-compose.yml')

    def __getFileLimit(self):
        limits = resource.getrlimit(resource.RLIMIT_NOFILE)
        return limits[1]

    def list(self):
        meta = MySQLBackupMeta()
        backups = []
        for directory in self._resort.adapter('mysql').listFolders(): 
            backup = self.__parseBackup(directory, meta)
            backup.inject(backups)
            
        return backups

    def __parseBackup(self, directory, meta):
        backupName = os.path.basename(directory)

        infoContent = self._resort.adapter('mysql').fileContent(directory+'/xtrabackup_info').decode('utf-8')

        return MySQLBackup().name(backupName).meta(meta).parseInfo(infoContent)
