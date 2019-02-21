import peachy
import peachy.geo


class HidingSpot(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(x, y, width, height)
        self.group = 'hiding-spot interact'
        self.visible = False

    def render(self):
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
