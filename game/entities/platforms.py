import peachy
import peachy.geo
from game import config


class FallingPlatform(peachy.Entity, peachy.geo.Rect):

    STATE_STABLE = 0
    STATE_UNSTABLE = 1
    STATE_FALLING = 2

    FALL_DELAY = 60

    def __init__(self, x, y):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, 8, 8)
        self.solid = True

        self.state = FallingPlatform.STATE_STABLE
        self.timer = FallingPlatform.FALL_DELAY
        self.order = 2

    def render(self):
        if self.state == FallingPlatform.STATE_STABLE:
            peachy.graphics.set_color(160, 82, 45)
        else:
            peachy.graphics.set_color(165, 42, 42)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.state == FallingPlatform.STATE_STABLE:
            player = self.container.get_name('player')
            if self.collides(player, self.x, self.y - player.height):
                self.state = FallingPlatform.STATE_UNSTABLE

        elif self.state == FallingPlatform.STATE_UNSTABLE:
            self.timer -= 1
            if self.timer <= 0:
                self.solid = False
                self.state = FallingPlatform.STATE_FALLING

        elif self.state == FallingPlatform.STATE_FALLING:
            if self.velocity_y < config.MAX_GRAVITY:
                self.velocity_y += config.GRAVITY

        self.y += self.velocity_y
