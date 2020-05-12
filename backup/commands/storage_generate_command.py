from .command import Command

class StorageGenerateCommand(Command):
    def usePassword(self):
        return True

    def __init__(self):
        self._name = "storage:generate"
        self._description( 'Authenticate with the storagebox', '''
        This command will copy public keys over to the storagebox and even
        create them for you if you do not yet have them.
        ''')

    def run(self, parameters):
        self._storage.copyId()
        return 0
