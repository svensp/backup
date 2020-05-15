import argparse
import base64
import io
import os
import binascii
from .command import Command

class StorageGenerateKeyCommand(Command):
    def usePassword(self):
        return True

    def __init__(self):
        self._name = "storage:generate-key"
        self._secretTarget = 'backup-key.yaml'
        self._keyTarget = 'id_rsa'
        self._description( 'Authenticate with the storagebox', '''
        This command will copy public keys over to the storagebox and even
        create them for you if you do not yet have them.
        ''')

    def run(self, parameters):
        self.__parseArgs(parameters)

        if self.__isKey() and os.path.exists( self._keyTarget ):
            print('WARNING! '+self._keyTarget+' already exists')
            if not self._args.overwrite:
                return

        if self.__isSecret() and os.path.exists( self._secretTarget ):
            print('WARNING! '+self._secretTarget+' already exists')
            if not self._args.overwrite:
                return
            

        newKey = self._storage.generateId()
        self.__writePrivateKey(newKey)

        self._storage.copyId(privateKey=newKey)
        return 0

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser()
        parser.add_argument('--secret', action='store_true', help='Create kubernetes secret instead of regular secret key')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite key file if it already exists')
        self._args = parser.parse_args(parameters)
    
    def __writePrivateKey(self, privateKey):
        if self.__isSecret():
            privateKeyString = self.__privateKeyToString(privateKey)
            secretYaml = self.__formatAsSecret(privateKeyString)
            with open('backup-key.yaml', 'w') as f:
                f.write(secretYaml)
            return
        privateKey.write_private_key_file(self._keyTarget)

    def __isSecret(self):
        return self._args.secret

    def __isKey(self):
        return not self._args.secret

    def __privateKeyToString(self, privateKey):
        stringFile = io.StringIO()
        privateKey.write_private_key(stringFile)
        return stringFile.getvalue()

    def __formatAsSecret(self, privateKeyString ):
        privateKeyBytes = privateKeyString.encode() 
        base64Bytes = base64.b64encode( privateKeyBytes )
        base64Key = base64Bytes.decode()
        secretYaml = '''---
apiVersion: v1
kind: Secret
metadata:
  name: backup-key
data:
  id_rsa: ''' + base64Key
        return secretYaml
