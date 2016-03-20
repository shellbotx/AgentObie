import peachy
from peachy import PC, Scene

from game.entities import *
from game.scenes import *

class LightingScene(AgentObieScene):

    def __init__(self, world):
        super().__init__(world)

    def load(self):
        self.player = Player(75, 100)
        # self.player.change_gadget('INVISIBLE')
        self.player.change_gadget('TIME')
        self.entities.add(self.player)

        soldier = self.entities.add(Soldier(PC.width / 3, 100))
        self.entities.add(Solid(75, 150, PC.width / 2 - 150, 32)).visible = True

    def render(self):
        peachy.graphics.set_color_hex('#010101')
        peachy.graphics.draw_rect(0, 0, PC.width, PC.height)

        peachy.graphics.set_color_hex('#001144')

        for y in range(-8, PC.height / 2, 16):
            # peachy.graphics.set_color_hex('#000055')
            peachy.graphics.draw_line(0, y, PC.width, y)
            # peachy.graphics.set_color_hex('#001155')
            # peachy.graphics.draw_line(0, y + 1, PC.width, y + 1)
        for x in range(-9, PC.width / 2, 16):
            peachy.graphics.draw_line(x, 0, x, PC.height / 2)

        super().render()


class TestScene(AgentObieScene):

    def __init__(self, world):
        super().__init__(world)

    def load_tmx(self, path):
        super().load_tmx(path)
        for e in self.entities:
            if e.member_of('solid'):
                e.visible = True
        self.player.change_gadget('INVISIBLE')
        # self.entities.add(MessageBox(4, 184, 'TEST MESSAGE'))

    def render(self):
        peachy.graphics.set_color_hex('#000055')

        for x in range(-9, int(PC.width / 2), 16):
            peachy.graphics.draw_line(x, 0, x, PC.height / 2)
        for y in range(-8, int(PC.height / 2), 16):
            peachy.graphics.draw_line(0, y, PC.width, y)

        super().render()

