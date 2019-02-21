import peachy
import peachy.geo

from game.entities import Bullet


class Turret(peachy.Entity, peachy.geo.Rect):

    ACTIVE = 0
    INACTIVE = 1
    COOLDOWN = 15

    def __init__(self, x, y, facing_x, facing_y):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, 8, 8)
        self.state = Turret.INACTIVE

        self.facing_x = facing_x
        self.facing_y = facing_y

        self.shot_timer = Turret.COOLDOWN
        self.order = 8

    def activate(self):
        self.state = Turret.ACTIVE

    def deactivate(self):
        self.state = Turret.INACTIVE

    def render(self):
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_entity_rect(self)

    def shoot(self):
        bullet = Bullet(self.x, self.y, self.facing_x, self.facing_y, 4)
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y
        bullet.order = 7
        self.container.add(bullet)

    def update(self):
        if self.state == Turret.ACTIVE:
            self.shot_timer -= 1
            if self.shot_timer <= 0:
                self.shoot()
                self.shot_timer = Turret.COOLDOWN
