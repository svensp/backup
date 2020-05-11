import configparser
import os
import resource
import shutil
import subprocess
import tarfile
import tempfile
import pyAesCrypt

class Finder():
    def backups(self, backups):
        self.backups = backups
        return self

class Sorter():
    def sort(self, backups):
        return sorted(backups, key=lambda backup: backup._name)

class LatestFinder(Finder):
    def __init__(self, sorter=Sorter()):
        self._sorter = sorter

    def find(self, backups):
        sortedBackups = self._sorter.sort(backups)
        return sortedBackups[-1]

class LatestFullFinder(Finder):
    def __init__(self, sorter=Sorter()):
        self._sorter = sorter

    def find(self, backups):
        fullBackups = []
        for backup in backups:
            if not backup.isFull():
                continue
            fullBackups.append(backup)

        sortedFullBackups = self._sorter(fullBackups)
        return sortedFullBackups[-1]
                

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

    def printRecursive(self, indent = 0):
        self.print()

        for child in self.getChildren():
            if child is self:
                continue
            child.printRecursive(indent + 2)
                

    def getHistory(self):
        history = [self]

        parent = self.getParent()
        while parent:
            history.append(parent)
            parent = parent.getParent()

        history.reverse()
        fullBackup = history.pop(0)
        return [ fullBackup, history ]
            

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
        self._specialNames = {
                'latest-full-backup': LatestFullFinder(),
                'latest-backup': LatestFinder(),
                }


    def resort(self, resort):
        self._resort = resort
        return self

    def incrementalBackup(self, name, parentName, dataDir):
        parent = self.find(parentName)

        return self.__backup(name, dataDir, parent._endingPoint)

    def fullBackup(self, name, dataDir):
        return self.__backup(name, dataDir)

    def __backup(self, name, dataDir, baseLsn = None):
        dataDirAbsolute = os.path.abspath(dataDir)
        fileLimit = self.__getFileLimit()
        with tempfile.TemporaryDirectory() as tempDirectory:
            backupDirectory = tempDirectory+'/backup'
            os.mkdir(backupDirectory)
            command = [
                'mariabackup',
                '--backup',
                '--datadir='+dataDirAbsolute,
                '--target-dir='+backupDirectory,
                '--host='+self._mysqlHost,
                '--user='+self._mysqlUsername,
                '--password='+self._mysqlPassword,
                '--port='+self._mysqlPort,
                ]
            if baseLsn:
                command.append('--incremental-lsn='+str(baseLsn))
                
            completedProcess = subprocess.run(command, check=True)
            self.__extractBackupInfo(backupDirectory, tempDirectory)
            tarFile = self.__compressBackup(backupDirectory, tempDirectory)
            self.__encryptBackup(tarFile)
            self.__uploadBackup(tempDirectory, name)
        return self

    def __extractBackupInfo(self, backupDirectory, tempDirectory):
            shutil.copy(backupDirectory+'/xtrabackup_info', tempDirectory+'/xtrabackup_info')

    def __compressBackup(self, backupDirectory, tempDirectory):
        tarFilePath = tempDirectory+'/backup.tar.bz2'
        tar = tarfile.open(tarFilePath, 'w:bz2')
        tar.add(backupDirectory, 'backup')
        tar.close()
        shutil.rmtree(backupDirectory)
        return tarFilePath

    def __encryptBackup(self, tarFilePath):
        pyAesCrypt.encryptFile(tarFilePath, tarFilePath+'.aes', self._password, self._bufferSize)
        os.remove(tarFilePath)

    def __uploadBackup(self, backupDirectory, name):
        self._resort.adapter('mysql').upload(backupDirectory, name)

    def find(self, name):
        availableBackups = self.list()
        for backup in availableBackups:
            if backup.isNamed(name):
                return backup
        raise BackupNotFoundException()

    def restore(self, name, dataDir, port=8080):
        dataDirAbsolute = os.path.abspath(dataDir)
        backup = self.find(name)
        fullBackup, history = backup.getHistory()
        self.__restoreFullBackup(fullBackup, dataDirAbsolute)
        self.__restoreIncrementalBackups(history, dataDirAbsolute)

        self.__copyDockerCompose(dataDirAbsolute+'/backup/docker-compose.yml', port)

    def __restoreFullBackup(self, backup, dataDir):
        self.__downloadAndExtract(backup, dataDir)
        completedProcess = subprocess.run([
            'mariabackup',
            '--prepare',
            '--target-dir='+dataDir+'/backup',
            ], check=True)

    def __restoreIncrementalBackups(self, backups, dataDir):
        for backup in backups:
            self.__restoreIncrementalBackup(backup, dataDir)

    def __restoreIncrementalBackup(self, backup, dataDir):
        with tempfile.TemporaryDirectory(dir=dataDir) as tempDir:
            self.__downloadAndExtract(backup, tempDir)
            completedProcess = subprocess.run([
                'mariabackup',
                '--prepare',
                '--target-dir='+dataDir+'/backup',
                '--incremental-dir='+tempDir+'/backup'
                ], check=True)

    def __downloadAndExtract(self, backup, targetDirectory):
        self._resort.adapter('mysql').download(backup._name, targetDirectory)
        tarFilePath = targetDirectory+'/backup.tar.bz2'
        self.__decryptBackup(tarFilePath)
        self.__unpackBackup(tarFilePath, targetDirectory)

    def __decryptBackup(self, tarFilePath):
        encryptedPath = tarFilePath+'.aes'
        pyAesCrypt.decryptFile(encryptedPath, tarFilePath, self._password, self._bufferSize)
        os.remove(encryptedPath)

    def __unpackBackup(self, tarFilePath, dataDir):
        tar = tarfile.open(tarFilePath, 'r:bz2')
        tar.extractall(dataDir)
        os.remove(tarFilePath)

    def __copyDockerCompose(self, target, port):
        with open(self._assetBase+'/docker-compose.yml', 'r') as file:
            dockerCompose = file.read()
        dockerCompose = dockerCompose.replace('%%PORT%%', str(port))
        with open(target, 'w') as file:
            file.write(dockerCompose)

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
