import peachy
from peachy import PC, Scene

from game.entities import *
from game.scenes import *

class LightingScene(AgentObieScene):

    def __init__(self, world):
        super(LightingScene, self).__init__(world)
        self.world = world

    def load(self):
        self.player = Player(50, 0)
        self.player.change_gadget('INVISIBLE')
        self.entities.add(self.player)

        soldier = self.entities.add(Soldier(PC.width / 4, 0))
        self.entities.add(Solid(50, 200, PC.width / 2 - 100, 32)).visible = True

class TestScene(AgentObieScene):

    def __init__(self, world):
        super(TestScene, self).__init__(world)
        self.world = world

    def load_tmx(self, path):
        super(TestScene, self).load_stage(self, path)
        for e in self.entities:
            if e.member_of('solid'):
                e.visible = True
        self.player.change_gadget('TIME')
        # self.entities.add(MessageBox(4, 184, 'TEST MESSAGE'))

    def render(self):
        peachy.graphics.set_color_hex('#000055')

        for x in xrange(-9, PC.width / 2, 16):
            peachy.graphics.draw_line(x, 0, x, PC.height / 2)
        for y in xrange(-8, PC.height / 2, 16):
            peachy.graphics.draw_line(0, y, PC.width, y)

        super().render(self)

