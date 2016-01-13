import peachy
from game.utility import collision_resolution

GRAVITY = 0.2
MAX_GRAVITY = 9

class PushBlock(peachy.Entity):

    def __init__(self, x, y):
        peachy.Entity.__init__(self, x, y)
        self.group = 'block liftable can-slow'
        self.solid = True
        self.width = 8
        self.height = 8
        self.slowed = False

    def render(self):
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

