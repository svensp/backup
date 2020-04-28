from .command import Command

class ResortsListCommand(Command):
    def __init__(self):
        self._name = "resorts:list"
        self._description( 'Print a list of available resorts')

    def storage(self, storage):
        self.__storage = storage
        return self

    def run(self, parameters):
        resorts = self.__storage.getResorts()
        for resort in resorts:
            resort.print()
