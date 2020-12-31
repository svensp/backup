from .command import Command
import subprocess

class MysqlCreateCommand(Command):
    def __init__(self):
        self._name = "mysql:create"
        self._description( 'Make sure mysql backup is available in a resort.  Create if necessary.')

    def run(self, parameters):
        if len(parameters) < 1:
            self.printHelp()
            return 1

        resortName = parameters[0]
        resort = self._storage.findResort(resortName)

        print("Creating mysql for resort"+resortName)
        resort.initMySQL()
        print("Created mysql for resort"+resortName)

    def printHelp(self):
        print("Usage:")
        print(self._name+" RESORTNAME\n")
        print("Make sure file backup is available in a resort")
        print("- RESORTNAME: The resort in which to make file backup available")
