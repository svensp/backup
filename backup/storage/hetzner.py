import os
from paramiko.client import SSHClient

class HetznerStorage:
    def __init__(self):
        self.__host = os.environ.get('HETZNER_STORAGEBOX')
        self.__port = int(os.environ.get('HETZNER_PORT', '22'))
        self.__username = os.environ.get('HETZNER_USER')
        self.__password = os.environ.get('HETZNER_PASSWORD')
        self.__hostKey = os.environ.get('HETZNER_HOSTKEY')
        self.__hostKeyType = os.environ.get('HETZNER_HOSTKEY_TYPE', 'ssh-rsa')
        self.__client = SSHClient()

    def load(self):
        self.__connect()
        self.__loadHostKey()
        pass

    def __connect(self):
        self.__client.connect(
                self.__host,
                self.__port,
                self.__username,
                self.__password
                )
        return self

    def __loadHostKey(self):
        self.__client._host_keys.add(
                self.__host,
                self.__hostKeyType,
                self.__hostKey)
        return self

    def getResorts(self):
        pass
