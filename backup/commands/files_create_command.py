from .command import Command
import subprocess

class FilesCreateCommand(Command):
    def __init__(self):
        self._name = "files:create"
        self._description( 'Make sure file backup is available in a resort.  Create if necessary.')

    def run(self, parameters):
        if len(parameters) < 1:
            self.printHelp()
            return 1

        copies = 2
        if len(parameters) > 1:
            lastParameterIndex = len(parameters) - 1
            lastParameter = parameters[lastParameterIndex]
            copies = int(lastParameter)
            
            
        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        resort.initBorg(copies);

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME [COPIES]\n")
        print("Make sure file backup is available in a resort")
        print("- RESORTNAME: The resort in which to make file backup available")
        print("- COPIES: The number of copies to create. Defaults to 2")
