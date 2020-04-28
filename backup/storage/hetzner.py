import os
from paramiko.transport import Transport
from paramiko.sftp_client import SFTPClient
from paramiko.hostkeys import HostKeyEntry
from .common import Resort

class HetznerStorage:
    def __init__(self):
        self.__host = os.environ.get('HETZNER_STORAGEBOX')
        self.__port = int(os.environ.get('HETZNER_PORT', '22'))
        self.__username = os.environ.get('HETZNER_USER')
        self.__password = os.environ.get('HETZNER_PASSWORD')
        self.__path = os.environ.get('HETNZER_PATH', '/backups')
        self.__hostKey = os.environ.get('HETZNER_HOSTKEY')
        self.__transport = Transport( (self.__host, self.__port) )

    def load(self):
        self.__connect()
        pass

    def __connect(self):
        hostKey = self.__getHostKey()
        self.__transport.connect(hostKey, self.__username, self.__password)
        self.__sftp = SFTPClient.from_transport(self.__transport)
        return self

    def __getHostKey(self):
        if self.__hostKey == 'any':
            return None

        hostKeyEntry = HostKeyEntry.from_line(self.__hostKey)
            
        return hostKeyEntry.key
            
    def createResort(self, resortName):
        self.__sftp.mkdir( self.__path+'/'+resortName, 0o755)

    def removeResort(self, resortName):
        self.__sftp.rmdir( self.__path+'/'+resortName)

    def getResorts(self):
        directories = self.__sftp.listdir( self.__path )

        resorts = []
        for directory in directories:
            resorts.append( self.buildResort(directory) )

        return resorts
    
    def buildResort(self, resortName):
        resort = Resort().name(resortName)

        resortDirectories = self.__sftp.listdir( self.__path+'/'+resortName )
        if 'mysql' in resortDirectories:
            resort.withMySQL()

        if 'postgres' in resortDirectories:
            resort.withPostgres()

        if 'files' in resortDirectories:
            resort.withFiles()

        return resort
