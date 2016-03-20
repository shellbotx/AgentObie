import peachy
from game.scenes import AgentObieScene
from game.entities import Player

class PierScene(AgentObieScene):

    def __init__(self, world):
        super().__init__(world)

        # Load backgrounds
        self.bga = peachy.fs.get_image('assets/img/bg_pier.png')
        # self.bgb = peachy.assets.get_image('assets/img/bg_pier_b')

    def load(self):
        self.player = Player(96, 128)
        self.load_tmx('assets/stage/pier_01.tmx')

    def render(self):
        peachy.graphics.draw(self.bga, 0, 0)
        super().render()
