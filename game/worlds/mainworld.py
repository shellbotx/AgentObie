import peachy

class MainWorld(peachy.World):
    NAME = 'main'

    def __init__(self):
        peachy.World.__init__(self, MainWorld.NAME)
