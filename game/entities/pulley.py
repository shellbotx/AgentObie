import peachy
import peachy.geo


class Pulley(peachy.Entity, peachy.geo.Rect):

    STATE_ACTIVE = 0
    STATE_INACTIVE = 1

    def __init__(self, x, y, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, 0, height)
        self.group = 'interact rope pulley'

        self.state = Pulley.STATE_INACTIVE
        self.player = None

    def render(self):
        if self.state == Pulley.STATE_INACTIVE:
            peachy.graphics.set_color(255, 0, 0)
        elif self.state == Pulley.STATE_ACTIVE:
            peachy.graphics.set_color(0, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        return
