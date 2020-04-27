class ResortsCommand:
    def storage(self, storage):
        self.__storage = storage
        return self

    def run(self):
        resorts = self.__storage.getResorts()
        for resort in resorts:
            print("- "+resort.getName())

    def printDescription(self):
        print("resorts - list available resorts")
