import configparser
import os.path

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
    def resort(self, resort):
        self._resort = resort
        return self

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

        backupHistory = self._resort.adapter('mysql').fileContent(directory+'/backup_history.txt').decode('utf-8')
        backupHistoryLines = backupHistory.split('\n')
        lastBackupLineIndex = len(backupHistoryLines) - 1
        lastBackupLine = backupHistoryLines[lastBackupLineIndex]
        if not lastBackupLine:
            lastBackupLineIndex = len(backupHistoryLines) - 2
            lastBackupLine = backupHistoryLines[lastBackupLineIndex]
            
        parent = lastBackupLine

        return MySQLBackup().name(backupName).full(isFullBackup).parent(parent)
