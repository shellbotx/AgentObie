import os
import peachy
from peachy import PC
from worlds import *

class AgentObieEngine(peachy.Engine):

    def __init__(self, debug):
        peachy.Engine.__init__(self, (640, 480), 'Agent Obie', debug=debug)

        self.add_world(MainWorld())
        self.add_world(GameWorld())
        self.add_world(CinemaWorld())

    def preload(self):
        peachy.fs.load_font('SourceCodePro@12', 'assets/SourceCodePro.ttf', 12)
        peachy.fs.load_font('SourceCodePro@16', 'assets/SourceCodePro.ttf', 16)
        peachy.fs.load_font('FiraMono', 'assets/FiraMono-Medium.ttf', 16)

        peachy.fs.load_image('PlayerSprite', 'assets/img/obie.png')
        peachy.fs.load_image('SoldierSprite', 'assets/img/soldier.png')

        peachy.graphics.set_font(peachy.fs.resources['SourceCodePro@16'])

    def exit(self):
        for world in self.worlds.value():
            self.world.close()
