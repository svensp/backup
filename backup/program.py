import sys
import os
from .config import Config

class Program:
    def help(self):
        print(sys.argv[0]+" COMMAND")

    def setUp(self):
        self.__config = Config()
        self.__config.parse(os.environ)

    def run(self):
        if len(sys.argv) <= 1:
            self.help()
            return 0

        self.setUp()
            
        return 0
