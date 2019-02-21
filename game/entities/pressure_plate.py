import peachy
import peachy.geo


class PressurePlate(peachy.Entity, peachy.geo.Rect):

    STATE_INACTIVE = 0
    STATE_ACTIVE = 1

    def __init__(self, x, y, width, on_press='', on_release='', down=''):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, 2)
        self.group = 'pressure'

        self.on_press = on_press
        self.on_release = on_release
        self.down = down

        self.state = PressurePlate.STATE_INACTIVE
        self.order = 2

    def render(self):
        if self.state == PressurePlate.STATE_INACTIVE:
            peachy.graphics.set_color(255, 0, 0)
        elif self.state == PressurePlate.STATE_ACTIVE:
            peachy.graphics.set_color(0, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        colliding_player = self.collides_groups(self.x, self.y,
                                                'player', 'block')

        if self.state == PressurePlate.STATE_INACTIVE:
            if colliding_player:
                exec(self.on_press)
                self.state = PressurePlate.STATE_ACTIVE

        elif self.state == PressurePlate.STATE_ACTIVE:
            if colliding_player:
                exec(self.down)
            else:
                exec(self.on_release)
                self.state = PressurePlate.STATE_INACTIVE
