import peachy
import peachy.geo


class Sensor(peachy.Entity):
    def __init__(self, x, y, width, height, gun_name):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.gun_name = gun_name
        self.activated = False

        self.order = 10

    def activate(self):
        sensor_gun = self.container.get_name(self.gun_name)
        sensor_gun.activate()
        self.activated = True

    def deactivate(self):
        sensor_gun = self.container.get_name(self.gun_name)
        sensor_gun.deactivate()
        self.activated = False

    def render(self):
        peachy.graphics.set_color(255, 0, 0, 125)
        peachy.graphics.draw_entity_rect(self)

    def update(self):
        player = self.collides_name('player')
        if self.activated and (player is None or player.invisible):
            self.deactivate()
        elif not self.activated and (player is not None and not player.invisible):
            self.activate()
