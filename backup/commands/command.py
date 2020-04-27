class Command:
    def register(self, dictionary):
        dictionary[self._name] = self
        return self

    def _description(self, shortDescription, longDescription = None):
        if longDescription is None:
            longDescription = shortDescription

        self._shortDescription = shortDescription
        self._longDescription = longDescription
            

    def printDescription(self):
        print(self._name+" - "+self._shortDescription)
        return self
