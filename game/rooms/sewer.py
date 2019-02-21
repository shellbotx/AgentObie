from game.entities import Player
from game.rooms import AgentObieRoom


class Sewer(AgentObieRoom):

    def __init__(self, world):
        super().__init__(world)

    def enter(self):
        self.player = Player(152, 0)
        self.load_tmx('assets/stage/sewer_01.tmx')
