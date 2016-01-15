import peachy
from worlds import *

class AgentObieEngine(peachy.Engine):

    def __init__(self, debug):
        peachy.Engine.__init__(self, (640, 480), 'Agent Obie', debug=debug)

        self.add_world(GameWorld())
        self.add_world(MainWorld())
        self.add_world(CinemaWorld())

    def play_scene(self, name):
        self.change_world(GameWorld)
        self.world.change_scene(name)

#def enter_level(self, level_name):
#    self.change_world(GameWorld.NAME)
#    self.world.change_level(level_name)
    
    def exit(self):
        for world in self.worlds.value():
            self.world.close()

