import os
import stat
from paramiko.transport import Transport
from paramiko.sftp_client import SFTPClient
from paramiko.rsakey import RSAKey
from paramiko.pkey import PublicBlob
from paramiko.hostkeys import HostKeyEntry
from paramiko.agent import Agent
from .common import Resort, NoSuchResortError
from ..adapters.borg import Borg
from ..adapters.mysql import MySQL

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
        self.uploadChunkSize = int(os.environ.get('UPLOAD_CHUNK_SIZE', '2097152'))
        self.downloadChunkSize = int(os.environ.get('DOWLOAD_CHUNK_SIZE', '2097152'))

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
        self.__rmdir(self.__path+'/'+resortName, True)

    def __rmdir(self, directory, verbose=False):
        print(directory)
        for entry in self.__sftp.listdir_attr( directory ):
            if stat.S_ISDIR(entry.st_mode):
                subdir = directory+'/'+entry.filename
                if verbose:
                    print("Recursing into "+subdir)
                self.__rmdir(subdir)
            else:
                filePath = directory+'/'+entry.filename
                if verbose:
                    print("Removing into "+filePath)
                self.__sftp.remove(filePath)
                
        if verbose:
            print("Removing "+directory)
            
        self.__sftp.rmdir(directory)

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
            resort.withMySQL( 
                    MySQL()
                    .resort(resort)
                    )

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

    def listFolder(self, path):
        pathParts = [
            self.__path,
            self._currentResort,
            self.currentAdapter,
            ]
        if path is not None:
            pathParts.append(path)
        path = '/'.join(pathParts) 
        return self.__sftp.listdir( path )

    def fileContent(self, path):
        pathParts = [
            self.__path,
            self._currentResort,
            self.currentAdapter,
            path,
            ]
        path = '/'.join(pathParts) 
        with self.__sftp.file( path ) as file:
            return file.read()

    def upload(self, localPath, remotePath, verbose=False):
        fullRemotePath = '/'.join([
            self.__path,
            self._currentResort,
            self.currentAdapter,
            remotePath,
            ])

        if os.path.isdir(localPath):
            self.__uploadDirectory(localPath, fullRemotePath, verbose)
        else:
            self.__uploadFile(localPath, fullRemotePath, verbose)

    def __uploadDirectory(self, localPath, remotePath, verbose=False):
        mustMake = True
        try:
            remotePathStatus = self.__sftp.stat(remotePath)
            if not stat.S_ISDIR(remotePathStatus.st_mode):
                mustMake = False
        except FileNotFoundError:
            pass
                
        if mustMake:
            self.__sftp.mkdir(remotePath)

        for localFileName in os.listdir( localPath ):
            localFilePath = localPath + '/' + localFileName
            remoteFilePath = remotePath + '/' + localFileName
            if os.path.isdir(localFilePath):
                if verbose:
                    print("Recursing into "+localFilePath+" as "+remoteFilePath)
                self.__uploadDirectory(localFilePath, remoteFilePath, verbose)
            else:
                self.__uploadFile(localFilePath, remoteFilePath, verbose)
        pass

    def __uploadFile(self, localPath, remotePath, verbose=False):
        if verbose:
            print("Uploading "+localPath+" as "+remotePath)
        with open(localPath, 'rb') as localFile:
            with self.__sftp.file(remotePath, 'w') as remoteFile:
                while True:
                    data = localFile.read(self.uploadChunkSize)
                    if not data:
                        break
                    remoteFile.write(data)

    def download(self, remotePath, localPath, verbose=False):
        fullRemotePath = '/'.join([
            self.__path,
            self._currentResort,
            self.currentAdapter,
            remotePath,
            ])
        pathStat = self.__sftp.stat(fullRemotePath)
        if stat.S_ISDIR(pathStat.st_mode):
            self.__downloadDirectory(fullRemotePath, localPath,  verbose)
        else:
            self.__downloadFile(fullRemotePath, localPath, verbose)

    def __downloadDirectory(self, remotePath, localPath, verbose=False):
        mustMake = True
        try:
            if os.path.isdir(localPath):
                mustMake = False
        except FileNotFoundError:
            pass
                
        if mustMake:
            os.mkdir(localPath)

        for remoteFileAttribute in self.__sftp.listdir_attr( remotePath ):
            fileName = remoteFileAttribute.filename
            localFilePath = localPath + '/' + fileName
            remoteFilePath = remotePath + '/' + fileName

            if stat.S_ISDIR(remoteFileAttribute.st_mode):
                if verbose:
                    print("Recursing into "+localFilePath+" as "+remoteFilePath)
                self.__downloadDirectory(remoteFilePath, localFilePath, verbose)
            else:
                self.__downloadFile(remoteFilePath, localFilePath, verbose)
        pass

    def __downloadFile(self, remotePath, localPath, verbose=False):
        if verbose:
            print("Downloading "+remotePath+" as "+localPath)
        with self.__sftp.file(remotePath, 'rb') as remoteFile:
            with open(localPath, 'wb') as localFile:
                while True:
                    data = remoteFile.read(self.downloadChunkSize)
                    if not data:
                        break
                    localFile.write(data)

    def generateId(self):
        return RSAKey.generate(4096)

    def copyId(self, privateKey = None):
        if '.ssh' not in self.__sftp.listdir('/'):
            self.__sftp.mkdir('/.ssh', 0o700)

        if not privateKey:
            privateKey = self.__loadKey()

        with self.__sftp.open('/.ssh/authorized_keys', 'r') as f:
            authorizedKeys = f.read()
        fileContent = authorizedKeys.decode('utf-8')

        if fileContent[ -1 ] != '\n':
            print("File does not end in newline - adding")
            with self.__sftp.open('/.ssh/authorized_keys', 'a+') as f:
                f.write('\n')

        rfcPublicKey = self.__publicRFC4716(privateKey)
        publicKey = self.__publicKey(privateKey)

        if rfcPublicKey not in fileContent:
            print("public key in rfc format not in authorized keys - inserting")
            with self.__sftp.open('/.ssh/authorized_keys', 'a+') as f:
                f.write(rfcPublicKey+'\n')
        else:
            print('public key in rfc format already present')

        if publicKey not in fileContent:
            print("public key not in authorized keys - inserting")
            with self.__sftp.open('/.ssh/authorized_keys', 'a+') as f:
                f.write(publicKey+'\n')
        else:
            print('public key already present')
            

    def __loadKey(self):
        if self.__keyFilePath == 'agent':
            return self.__loadFromAgent()

        try:
            return RSAKey.from_private_key_file(self.__keyFilePath)
        except FileNotFoundError:
            print("Failed to load "+self.__keyFilePath+" trying the ssh-agent.")
            return self.__loadFromAgent()

    def __loadFromAgent(self):
        print("Failed to load ssh key - trying to connect to ssh agent")
        agent = Agent()
        keys = agent.get_keys()
        if len(keys) == 0:
            raise KeyError("No keys found in the ssh agent. Did you add them with ssh-add?")
            
        return keys[0]
    
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
