from .command import Command

class ResortsCreateCommand(Command):
    def __init__(self):
        self._name = "resorts:create"
        self._description( 'create a new resport')

    def storage(self, storage):
        self.__storage = storage
        return self

    def run(self, parameters):
        if len(parameters) < 1:
            self.printHelp()
            return 1
            
        resortName = parameters[0]
        print("Creating resort "+resortName)
        self.__storage.createResort(resortName)
        print("Created")

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME\n")
        print("Create a new resort")
