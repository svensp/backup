import os
from paramiko.transport import Transport
from paramiko.sftp_client import SFTPClient
from paramiko.rsakey import RSAKey
from paramiko.pkey import PublicBlob
from paramiko.hostkeys import HostKeyEntry
from .common import Resort, NoSuchResortError
from ..adapters.borg import Borg

class HetznerStorage:
    def __init__(self):
        self.__host = os.environ.get('HETZNER_STORAGEBOX')
        self.__port = int(os.environ.get('HETZNER_PORT', '22'))
        self.__username = os.environ.get('HETZNER_USER')
        self.__password = os.environ.get('HETZNER_PASSWORD')
        self.__path = os.environ.get('HETNZER_PATH', '/backups')
        self.__hostKey = os.environ.get('HETZNER_HOSTKEY')
        defaultSSHKeyFilePath = os.environ.get('HOME')+"/.ssh/id_rsa"
        self.__keyFilePath = os.environ.get('HETZNER_SSHKEY', defaultSSHKeyFilePath)
        self.__transport = Transport( (self.__host, self.__port) )
        self._usePassword = False

    def load(self):
        self.__connect()
        pass

    def __connect(self):
        hostKey = self.__getHostKey()
        if self._usePassword:
            self.__transport.connect(hostKey, self.__username, self.__password)
        else:
            privateKey = self.__loadKey()
            self.__transport.connect(hostKey, self.__username, pkey=privateKey)

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

    def findResort(self, resortName):
        directories = self.__sftp.listdir( self.__path )

        if resortName not in directories:
            raise NoSuchResortError(resortName)

        return self.buildResort(resortName)

    def getResorts(self):
        directories = self.__sftp.listdir( self.__path )

        resorts = []
        for directory in directories:
            resorts.append( self.buildResort(directory) )

        return resorts
    
    def buildResort(self, resortName):
        resort = Resort().name(resortName).storage(self)
        return self.rebuildResort(resort)

    def rebuildResort(self, resort):
        resortPath = resort.appendName(self.__path+'/')

        resortDirectories = self.__sftp.listdir( resortPath )
        if 'mysql' in resortDirectories:
            resort.withMySQL()

        if 'postgres' in resortDirectories:
            resort.withPostgres()

        if 'files' in resortDirectories:
            path = '/'.join([
                resortPath,
                'files'
                ])
            resort.withBorg(
                    Borg()
                    .host(self.__host)
                    .port(23)
                    .path(path)
                    .user(self.__username)
                    .keyFilePath(self.__keyFilePath)
                    )

        return resort

    def resort(self, resortName):
        self._currentResort = resortName
        return self

    def adapter(self, adapterName):
        self.currentAdapter = adapterName
        return self

    def createAdapter(self, adapterName):
        self.__sftp.mkdir( self.__path+'/'+self._currentResort+'/'+adapterName, 0o755)
        return self

    def usePassword(self):
        self._usePassword = True
        return self
    
    def createFolder(self, folderName):
        path = '/'.join([
            self.__path,
            self._currentResort,
            self.currentAdapter,
            folderName
            ]) 
        self.__sftp.mkdir( path, 0o755)

    def copyId(self):
        if '.ssh' not in self.__sftp.listdir('/'):
            self.__sftp.mkdir('/.ssh', 0o700)

        privateKey = self.__loadKey()

        with self.__sftp.open('/.ssh/authorized_keys', 'r') as f:
            authorizedKeys = f.read()
        fileContent = str(authorizedKeys).replace('\\n', '\n')

        rfcPublicKey = self.__publicRFC4716(privateKey)
        publicKey = self.__publicKey(privateKey)

        if rfcPublicKey not in fileContent:
            print("public key in rfc format not in authorized keys - inserting")
            with self.__sftp.open('/.ssh/authorized_keys', 'a+') as f:
                f.write('\n'+rfcPublicKey)
        else:
            print('public key in rfc format already present')

        if publicKey not in fileContent:
            print("public key not in authorized keys - inserting")
            with self.__sftp.open('/.ssh/authorized_keys', 'a+') as f:
                f.write('\n'+publicKey)
        else:
            print('public key already present')
            

    def __loadKey(self):
        return RSAKey.from_private_key_file(self.__keyFilePath)
    
    def __publicRFC4716(self, privateKey):
        # NOte: rfc4716 says 72 bytes at most but ssh-keygen into rfc4716
        # creates 70 character lines
        publicKeyPart = '\n'.join(list(self.chunkstring(privateKey.get_base64(), 70)))

        key = '\n'.join([
            '---- BEGIN SSH2 PUBLIC KEY ----',
            publicKeyPart,
            '---- END SSH2 PUBLIC KEY ----'
        ])
        return key

    def chunkstring(self, string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))

    def __publicKey(self, privateKey):
        key = privateKey.get_name()
        key += ' '
        key += privateKey.get_base64()
        return key
