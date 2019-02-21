import peachy
from peachy import PC

from game.entities import *
from game.rooms import AgentObieRoom
from game.utility import *


class BackgroundTest(AgentObieRoom):

    def __init__(self, world):
        super().__init__(world)
        self.background = None
        self.foreground = None
        self.load_background('pier')

    def enter(self):
        self.player = self.add(Player(96, 320))
        self.add(Solid(0, 480 - 32, 640 / 2, 32)).visible = True
        self.add(Rope(32, 32, 0, 480)).visible = True

    def load_background(self, background):
        if background == 'pier':
            self.camera.max_width = 640
            self.camera.max_height = 480
            self.background = ParallaxBG(480, 240)
            self.background.create_layer(
                peachy.fs.get_image('assets/img/pier_bg_clouds.png'),
                peachy.geo.Point(-0.5, 0),
                True, False)
            self.background.create_layer(
                peachy.fs.get_image('assets/img/pier_bg.png'),
                peachy.utils.Point(-0.1, 0),
                True, False)
            self.background.create_layer(
                peachy.fs.get_image('assets/img/pier_fg_clouds.png'),
                peachy.utils.Point(-0.5, 0),
                True, False)

    def render(self):
        peachy.graphics.set_color(15, 56, 87)
        peachy.graphics.draw_rect(0, 0, 360, 240)
        self.background.render(self.camera.x * -1 / 16, 0)
        super().render()


class GenericTest(AgentObieRoom):

    def __init__(self, world):
        super().__init__(world)
        self.deb_visible = False

    def enter(self):
        self.player = self.add(Player(75, 100))

    def toggle_debug_visibility(self):
        self.deb_visible = not self.deb_visible

        for e in self.entities:
            if e.member_of('solid') or e.member_of('rope') or \
               e.member_of('ladder'):
                e.visible = self.deb_visible

    def render(self):
        peachy.graphics.set_color_hex('#040404')
        peachy.graphics.draw_rect(0, 0, PC().canvas_width, PC().canvas_height)
        peachy.graphics.set_color_hex('#000055')

        for x in range(-9, int(PC().canvas_width / 2), 16):
            peachy.graphics.draw_line(x, 0, x, PC().canvas_height / 2)
        for y in range(-8, int(PC().canvas_height / 2), 16):
            peachy.graphics.draw_line(0, y, PC().canvas_width, y)

        super().render()

    def update(self):
        if peachy.utils.Key.pressed('1'):
            self.player.change_gadget('NONE')
        elif peachy.utils.Key.pressed('2'):
            self.player.change_gadget('INVISIBLE')
        elif peachy.utils.Key.pressed('3'):
            self.player.change_gadget('TIME')
        elif peachy.utils.Key.pressed('4'):
            self.player.change_gadget('STUN')
        elif peachy.utils.Key.pressed('5'):
            self.player.change_gadget('FLASH')
        elif peachy.utils.Key.pressed('6'):
            self.player.change_gadget('DUPLICATE')

        if peachy.utils.Key.pressed('F2'):
            self.toggle_debug_visibility()
        super().update()


class DogTest(GenericTest):

    def __init__(self, world):
        super().__init__(world)

    def enter(self):
        super().enter()
        self.add(Dog(PC().canvas_width / 3, 100))
        self.add(Solid(75, 150, PC().canvas_width / 2 - 150, 32)).visible = True


class SoldierTest(GenericTest):

    def __init__(self, world):
        super().__init__(world)

    def enter(self):
        print("INI")
        super().enter()
        self.add(Soldier(PC().canvas_width / 3, 100))
        self.add(Solid(75, 150, PC().canvas_width / 2 - 150, 32)).visible = True
