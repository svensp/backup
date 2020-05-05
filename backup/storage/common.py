class Resort:
    def __init__(self):
        self._mysql = False
        self._postgres = False
        self._borg = False

    def name(self, name):
        self._name = name
        return self

    def appendName(self, text):
        return text+self._name
        return self

    def storage(self, storage):
        self._storage = storage
        return self

    def withMySQL(self, mysql):
        self._mysql = mysql
        return self

    def withPostgres(self):
        self._postgres = True
        return self

    def passAdapters(self, receiver):
        try:
            receiver.setBorg(self._borg)
        except AttributeError:
            pass

        try:
            receiver.setMySQL(self._mysql)
        except AttributeError:
            pass

        try:
            receiver.setPostgres(self._postgres)
        except AttributeError:
            pass

    def initMySQL(self, copies):
        try:
            self._storage.resort(self._name).createAdapter('mysql')
        except OSError:
            print("MySQL already exists. Ignoring")
        self._storage.rebuildResort(self)


    def initBorg(self, copies):
        try:
            self._storage.resort(self._name).createAdapter('files')
        except OSError:
            print("Files already exists. Ignoring")
        self._storage.rebuildResort(self)

        self._borg.init(copies)

    def withBorg(self, borg):
        borg.resort(self)
        self._borg = borg
        return self

    def createFolder(self, folderName):
        self._storage.resort(self._name).adapter(self._currentAdapter).createFolder(folderName)
        return self

    def listFolders(self, path=None):
        return self._storage.resort(self._name).adapter(self._currentAdapter).listFolder(path)

    def fileContent(self, path):
        return self._storage.resort(self._name).adapter(self._currentAdapter).fileContent(path)

    def adapter(self, adapater):
        self._currentAdapter = adapater
        return self

    def print(self):
        print("- "+self._name)

        if self._borg:
            print("  - borg filebackup")

        if self._mysql:
            print("  - mysql")

        if self._postgres:
            print("  - postgres")

class Error(Exception):
    pass

class NoSuchResortError(Error):
    def __init__(self, resortName):
        self.resortName = resortName
