import peachy
import peachy.utils
from peachy import PC

from game.entities import Player
from game.rooms import AgentObieRoom
from game.utility import ParallaxBG


class Pier(AgentObieRoom):

    def __init__(self, world):
        super().__init__(world)
        self.inside = False

        self.background = None
        self.foreground = None
        self.foreground_timer = None

        self.pause_menu_name = 'THE PIER'

    def _init_scenery(self):
        RM = PC().resources
        self.background = ParallaxBG(480, 240)
        self.background.create_layer(
            RM.get_resource_by_name('PierBackground_Clouds'),
            peachy.geo.Point(-0.5, 0),
            True, False)
        self.background.create_layer(
            RM.get_resource_by_name('PierBackground'),
            peachy.geo.Point(-0.1, 0),
            True, False)
        self.background.create_layer(
            RM.get_resource_by_name('PierForeground_Clouds'),
            peachy.geo.Point(-0.5, 0),
            True, False)

        self.foreground_timer = peachy.utils.Counter(
            0, 8, enable_repeat=True, enable_pingpong=True, step=0.05)
        self.foreground = RM.get_resource_by_name('PierForeground_Water')

    def enter(self):
        PC().resources.activate_bundle('PierResources')
        if self.background is None or self.foreground is None:
            self._init_scenery()

        self.player = Player(96, 180)
        self.load_tmx('stage/pier_01.tmx')

    def exit(self):
        PC().resources.deactivate_bundle('PierResources')
        # Release resources
        self.background = None
        self.foreground = None

    def pause(self):
        super().pause()
        # self.background.pause()

    def resume(self):
        super().resume()
        # self.background.resume()

    def load_tmx(self, path, _reload=False, checkpoint=False):
        super().load_tmx(path, _reload, checkpoint)
        self.inside = 'INSIDE' in self.stage_data.properties

    def render(self):
        if self.inside:
            super().render()
        else:
            peachy.graphics.set_color(15, 56, 87)
            peachy.graphics.draw_rect(0, 0, 360, 240)
            # self.background.render(self.camera.x * -1 / 16, 0)
            super().render()

            # Simulate waves
            if not self.paused:
                self.foreground_timer.advance()
                peachy.graphics.draw(self.foreground, 0,
                                     self.camera.height - 232 -
                                     self.foreground_timer.current)
