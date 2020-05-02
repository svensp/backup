class Files:
    def __init__(self):
        self._port = 22

    def host(self, host):
        self._host = host
        return self

    def port(self, port):
        self._port = port
        return self

    def path(self, path):
        self._path = path
        return self
