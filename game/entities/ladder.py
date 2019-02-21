import peachy
import peachy.geo


class Ladder(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, 8, height)
        self.group = 'interact ladder'

        self.visible = False

        self.order = 2

    def render(self):
        peachy.graphics.set_color(63, 52, 4)
        peachy.graphics.draw_entity_rect(self)

    def update(self):
        player = self.container.get_name('player')
        if player.y + player.height - 1 < self.y:
            self.solid = True
        else:
            self.solid = False
