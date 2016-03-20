import peachy
from game.scenes import *

class CinemaWorld(peachy.World):
    NAME = 'cinema'

    def __init__(self):
        peachy.World.__init__(self, CinemaWorld.NAME)
        self.scene = None

    def load_scene(self, scene_name):
        if scene_name == 'SCENE01':
            self.scene = Scene01()
        elif scene_name == 'TEST':
            self.scene = TestScene()

    def render(self):
        self.scene.render()

    def update(self):
        # TODO skip cutscene button
        self.scene.update()
