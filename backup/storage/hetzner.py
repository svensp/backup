import os
from paramiko.transport import Transport
from paramiko.sftp_client import SFTPClient
from paramiko.pkey import PKey
from .common import Resort

class HetznerStorage:
    def __init__(self):
        self.__host = os.environ.get('HETZNER_STORAGEBOX')
        self.__port = int(os.environ.get('HETZNER_PORT', '22'))
        self.__username = os.environ.get('HETZNER_USER')
        self.__password = os.environ.get('HETZNER_PASSWORD')
        self.__path = os.environ.get('HETNZER_PATH', '/backups')
        self.__hostKey = PKey(data=os.environ.get('HETZNER_HOSTKEY'))
        self.__hostKeyType = data=os.environ.get('HETZNER_HOSTKEY_TYPE', 'ssh-rsa')
        self.__transport = Transport( (self.__host, self.__port) )

    def load(self):
        self.__connect()
        pass

    def __connect(self):
        self.__transport.connect(None, self.__username, self.__password)
        self.__sftp = SFTPClient.from_transport(self.__transport)
        return self

    def getResorts(self):
        directories = self.__sftp.listdir( self.__path )

        resorts = []
        for directory in directories:
            resorts.append( Resort().name(directory) )
        return resorts
