from game.scenes import AgentObieScene
from game.entities import Player

class SewerScene(AgentObieScene):
    
    def __init__(self, world):
        AgentObieScene.__init__(self, world)
        self.world = world

    def load(self):
        self.player = Player(152, 0)
        self.load_tmx('assets/stage/sewer_01.tmx')
