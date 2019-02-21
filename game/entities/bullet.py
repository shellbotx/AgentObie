import peachy
import peachy.geo


class Bullet(peachy.Entity):

    def __init__(self, x, y, direction_x, direction_y, speed):
        super(peachy.Entity).__init__()
        super(peachy.geo.Rect).__init__(x, y, 4, 4)
        self.group = 'can-slow bullet'

        self.direction_x = direction_x
        self.direction_y = direction_y

        self.speed = speed
        self.slowed = False

    def render(self):
        if self.slowed:
            peachy.graphics.set_color(0, 0, 255)
        else:
            peachy.graphics.set_color(255, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        player = self.container.get_name('player')

        speed = self.speed
        if self.slowed:
            speed /= 4

        self.x += speed * self.direction_x
        self.y += speed * self.direction_y

        if self.collides_solid() or self.collides_group('solid'):
            self.destroy()
        if self.collides(player, self.x, self.y):
            player.kill(self)
            self.destroy()

    def GADGET_slow(self):
        self.slowed = True

    def GADGET_revert(self):
        self.slowed = False
