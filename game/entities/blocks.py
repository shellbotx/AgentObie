import peachy
import peachy.geo
from game.config import GRAVITY, MAX_GRAVITY
from game.utility import collision_resolution


class PushBlock(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y):
        super(peachy.Entity).__init__()
        super(peachy.geo.Rect).__init__(x, y, 8, 8)
        self.group = 'block liftable can-slow'
        self.solid = True
        self.slowed = False
        self.order = 2

    def render(self):
        # Placeholder rendering
        peachy.graphics.set_color(0, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        temp_x = self.x
        temp_y = self.y

        if self.velocity_y < MAX_GRAVITY:
            self.velocity_y += GRAVITY

        if self.slowed:
            if self.velocity_y > 1:
                self.velocity_y = 1

        temp_x += self.velocity_x
        temp_y += self.velocity_y

        c, temp_x, temp_y, self.velocity_x, self.velocity_y = \
            collision_resolution(self, temp_x, temp_y)

        self.x = temp_x
        self.y = temp_y

    def GADGET_slow(self):
        self.slowed = True

    def GADGET_revert(self):
        self.slowed = False
