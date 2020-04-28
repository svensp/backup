from .command import Command

class ResortsRemoveCommand(Command):
    def __init__(self):
        self._name = "resorts:remove"
        self._description( 'remove a resort')

    def storage(self, storage):
        self.__storage = storage
        return self

    def run(self, parameters):
        if len(parameters) < 1:
            print("No confirmation given.")
            print("Please add the flag '-y' to confirm you are sure you want to delete the resort and it's entire content")
            self.printHelp()
            return 2

        if len(parameters) < 2:
            self.printHelp()
            return 1

        flag = parameters[0]
        if flag != "-y":
            print("Confirm flag ist not '-y' - Aborting")
            return 3
            
            
        resortName = parameters[1]
        print("Removing resort "+resortName)
        self.__storage.removeResort(resortName)
        print("removed")

    def printHelp(self):
        print("Usage:")
        print(self._name+" -y RESORTNAME\n")
        print("Delete a resort with all its content")
