import datetime
import dateutil.parser
import json
import os
import subprocess
from prometheus_client import Gauge

class FileBackup():
    def parse(self, dict):
        self._name = dict['name']
        self._time = dateutil.parser.isoparse(dict['time'])
        return self

    def getName(self):
        return self._name

    def inject(self, list):
        list.append(self)
        return self

    def setTimestamp(self, gauge):
        gauge.set(self._time.timestamp())
        return self

    def print(self):
        print('- '+self._name+' made at '+str(self._time) )

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
        repositoryNumber = 1
        while repositoryNumber <= copies:
            self.__createRepository(repositoryNumber)
            repositoryNumber += 1
        print("Created")

        repositoryNumber = 1
        while repositoryNumber <= copies:
            self.__initRepository(repositoryNumber)
            repositoryNumber += 1

    def __createRepository(self, repositoryNumber):
        try:
            fileRepository = 'repo'+str(repositoryNumber)
            self._resort.adapter('files').createFolder(fileRepository)
            print("Folder for Repository "+str(repositoryNumber)+" created")
        except OSError:
            print("Folder for Repository "+str(repositoryNumber)+" already exists")

    def __initRepository(self, repositoryNumber):
        repo = self.__makeRepo(repositoryNumber)
        print("Initializing Repository "+str(repositoryNumber))
        completedProcess = self.command([
            'init',
            '-e',
            self._encryptionMode,
            repo
            ], repositoryNumber)
        if completedProcess.returncode != 0:
            print("Process did not return success:")
            print("Code: "+ str(completedProcess.returncode))
            print( str(completedProcess.stdout) )
            print( str(completedProcess.stderr) )
            return self
        print("Initialized Repository "+str(repositoryNumber)+" successfully")
        return self

    def remove(self, name, repositoryNumber):
        self.__findBackup(name, repositoryNumber)
        print("Removing backup "+name+" from Repository "+str(repositoryNumber))
        completedProcess = self.command([
            'delete',
            '::'+name,
            ], repositoryNumber)
        if completedProcess.returncode != 0:
            print("Process did not return success:")
            print("Code: "+ str(completedProcess.returncode))
            print( completedProcess.stdout.decode('utf-8') )
            print( completedProcess.stderr.decode('utf-8') )
            return self
        print("Removal of "+name+" from Repository "+str(repositoryNumber)+" finished successfully")
        return self

    def backup(self, name, target, repositoryNumber):
        print("Backing up "+target+" to Repository "+str(repositoryNumber))
        completedProcess = self.command([
            'create',
            '::'+name,
            '.'
            ], repositoryNumber, directory=target, capture_output=False)
        print("Backup of "+target+" to Repository "+str(repositoryNumber)+" finished successfully")
        return self

    def umount(self, target):
        completedProcess = subprocess.run([
            'fusermount',
            '-u',
            target
            ],
            capture_output=True
            )
        if completedProcess.returncode != 0:
            print("Failed to unmount "+target)
            print("Code: "+ str(completedProcess.returncode))
            print( completedProcess.stdout.decode('utf-8') )
            print( completedProcess.stderr.decode('utf-8') )
            return self

    def mount(self, name, target, repositoryNumber):
        print("Mounting backup "+name+" from Repository "+str(repositoryNumber)+' to '+target)
        print("The borg mount is run in foreground to facilitate usage inside Docker")
        print("Please cancel the program with an interrupt (control+c) after you are done.")
        completedProcess = self.command([
            'mount',
            '-f',
            '::'+name,
            target
            ], repositoryNumber)
        if completedProcess.returncode != 0:
            print("Process did not return success:")
            print("Code: "+ str(completedProcess.returncode))
            print( completedProcess.stdout.decode('utf-8') )
            print( completedProcess.stderr.decode('utf-8') )
            return self
        print("Mounted backup "+name+" from Repository "+str(repositoryNumber)+' to '+target)
        return self


    def list(self, repositoryNumber):
        completedProcess = self.command([
            'list',
            '--json',
            '::'
            ], repositoryNumber, check=False)
        if completedProcess.returncode != 0:
            print("Process did not return success:")
            print("Code: "+ str(completedProcess.returncode))
            print( completedProcess.stdout.decode('utf-8') )
            print( completedProcess.stderr.decode('utf-8') )
            raise ValueError("List process failed")
        output = completedProcess.stdout.decode('utf-8')
        decodedOutput = json.loads(output)
        return self.__archivesToBackups(decodedOutput['archives'])

    def __archivesToBackups(self, list):
        backups = []
        for archive in list:
            backup = FileBackup().parse(archive)
            backup.inject(backups)
        sortedBackups = sorted(backups, key=lambda backup : backup._time)
        return sortedBackups
            
            
    def restore(self, name, target, repositoryNumber):
        backup = self.__findBackup(name, repositoryNumber)
        print("Restoring backup "+backup.getName()+" from Repository "+str(repositoryNumber)+' to '+target)
        completedProcess = self.command([
            'extract',
            '::'+backup.getName()
            ], repositoryNumber, directory=target)

    def prune(self, repositoryNumber):
        repo = self.__makeRepo(repositoryNumber)
        print("Pruning file backups in repository "+repositoryNumber)
        completedProcess = self.command([
            'prune',
            '--keep-daily=14',
            '--keep-weekly=6',
            '--keep-monthly=6',
            '::'
            ], repositoryNumber)
        if completedProcess.returncode != 0:
            print("Process did not return success:")
            print("Code: "+ str(completedProcess.returncode))
            print( completedProcess.stdout.decode('utf-8') )
            print( completedProcess.stderr.decode('utf-8') )
            return self
        return completedProcess.stdout.decode('utf-8')

    def command(self, args, repoNumber, directory=None, check=True,
            capture_output=True):
        if directory is None:
            directory = os.getcwd()

        return subprocess.run(
                ['borgbackup'] + args,
                capture_output=capture_output,
                env={
                'BORG_NEW_PASSPHRASE': self._borgPassword,
                'BORG_PASSPHRASE': self._borgPassword,
                'BORG_REPO': self.__makeRepo(repoNumber),
                'SSH_AUTH_SOCK': os.environ.get('SSH_AUTH_SOCK', ''),
                'BORG_RSH': "ssh -o StrictHostKeyChecking=accept-new -i "+self._keyFilePath
                }, cwd=directory, check=check)

    def __makeRepo(self, number):
        return 'ssh://'+self._user+'@'+self._host+':'+str(self._port)+'/.'+self._path+'/repo'+str(number)

    def __findBackup(self, target, repositoryNumber):
        if target == 'latest':
            return self.list(repositoryNumber)[-1]
            
        return target

    def getRepositories(self):
        repos = []
        for directoryName in self._resort.adapter('files').listFolders():
            start = len('repo')
            end = len(directoryName)
            repos.append( directoryName[start:end] )

        return repos
    
    def scrape(self, gauge):
        for repositoryNumber in self.getRepositories():
            try:
                backup = self.__findBackup('latest', repositoryNumber)
            except IndexError:
                gauge.labels(self._resort._name, 'repository_'+str(repositoryNumber)).set(0)
                continue

            backup.setTimestamp( gauge.labels(self._resort._name, 'repository_'+str(repositoryNumber)) )

        return self
