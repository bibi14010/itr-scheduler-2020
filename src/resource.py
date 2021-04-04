Class Resource:
    def __init__(self, name:str):
        self.name = name
        self.inuse = False

    def get_resource(self):
        self.inuse = True

    def release_resource(self):
        self.inuse = False



