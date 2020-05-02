import os
import subprocess

class Borg:
    def __init__(self):
        self._port = 23
        self._borgPassword = os.environ.get('BORG_PASSWORD')
        self._encryptionMode = 'repokey-blake2'

    def resort(self, resort):
        self._resort = resort
        return self

    def user(self, user):
        self._user = user
        return self

    def host(self, host):
        self._host = host
        return self

    def port(self, port):
        self._port = port
        return self

    def path(self, path):
        self._path = path
        return self

    def keyFilePath(self, keyFilePath):
        self._keyFilePath = keyFilePath
        return self

    def borgPassword(self, borgPassword):
        self._borgPassword = borgPassword
        return self

    def init(self, copies):
        resortNumber = 1
        while resortNumber <= copies:
            self.__createRepository(resortNumber)
            resortNumber += 1
        print("Created")

        resortNumber = 1
        while resortNumber <= copies:
            self.__initRepository(resortNumber)
            resortNumber += 1

    def __createRepository(self, resortNumber):
        try:
            fileRepository = 'repo'+str(resortNumber)
            self._resort.adapter('files').createFolder(fileRepository)
            print("Folder for Repository "+str(resortNumber)+" created")
        except OSError:
            print("Folder for Repository "+str(resortNumber)+" already exists")

    def __initRepository(self, resortNumber):
        repo = self.__makeRepo(resortNumber)
        print("Initializing Repository "+str(resortNumber))
        print(self._keyFilePath)
        completedProcess = subprocess.run([
            'borgbackup',
            'init',
            '-e',
            self._encryptionMode,
            repo
            ], capture_output=True, env={
                'BORG_NEW_PASSPHRASE': self._borgPassword,
                'BORG_RSH': "ssh -o StrictHostKeyChecking=accept-new -i "+self._keyFilePath
                })
        if completedProcess.returncode != 0:
            print("Process did not return success:")
            print("Code: "+ str(completedProcess.returncode))
            print( str(completedProcess.stdout) )
            print( str(completedProcess.stderr) )
            return self
        print("Initialized Repository "+str(resortNumber)+" successfully")
        return self

    def __makeRepo(self, number):
        return 'ssh://'+self._user+'@'+self._host+':'+str(self._port)+'/.'+self._path+'/repo'+str(number)
