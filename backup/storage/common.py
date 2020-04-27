class Resort:
    def __init__(self):
        self.__mysql = False
        self.__postgres = False
        self.__files = False

    def name(self, name):
        self.__name = name
        return self

    def withMySQL(self):
        self.__mysql = True
        return self

    def withPostgres(self):
        self.__postgres = True
        return self

    def withFiles(self):
        self.__files = True
        return self

    def print(self):
        print("- "+self.__name)

        if self.__files:
            print("  - files")

        if self.__mysql:
            print("  - mysql")

        if self.__postgres:
            print("  - postgres")
