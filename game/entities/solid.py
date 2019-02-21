import peachy
import peachy.geo
from game.utility import get_line_segments


class Solid(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.group = 'solid opaque'
        self.solid = True
        self.visible = False

        self.segments = get_line_segments(self)

    def render(self):
        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def refresh_segments(self):
        self.segments = get_line_segments(self)
