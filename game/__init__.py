import os
import peachy
# from peachy.assets import load_font
from worlds import *

class AgentObieEngine(peachy.Engine):

    def __init__(self, debug):
        peachy.Engine.__init__(self, (640, 480), 'Agent Obie', debug=debug)

        self.add_world(MainWorld())
        self.add_world(GameWorld())
        self.add_world(CinemaWorld())

    def preload(self):
        font = peachy.graphics.Font("assets/SourceCodePro.ttf", 12)
        peachy.graphics.set_font(font)

    def exit(self):
        for world in self.worlds.value():
            self.world.close()
