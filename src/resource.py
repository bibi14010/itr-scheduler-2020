class Resource:
    def __init__(self, name:str, inuse):
        self.name = name
        self.inuse = False
        self.used_by = None

    def get_resource(self):
        self.inuse = True

    def release_resource(self):
        self.inuse = False





