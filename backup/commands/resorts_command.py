from .command import Command

class ResortsCommand(Command):
    def __init__(self):
        self._name = "resorts"
        self._description( 'Print a list of available resorts')

    def storage(self, storage):
        self.__storage = storage
        return self

    def run(self):
        resorts = self.__storage.getResorts()
        for resort in resorts:
            print("- "+resort.getName())
