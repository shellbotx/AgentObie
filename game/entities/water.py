import peachy
import peachy.geo


class Flooder(peachy.Entity):

    def __init__(self, x, y, width, timeout):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, 2)
        self.timeout = timeout
        self.open = False

    def render(self):
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)


class FlowingWater(peachy.Entity, peachy.geo.Rect):
    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.group = 'water'

    def render(self):
        peachy.graphics.set_color(0, 0, 255, 200)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        player = self.collides_name('player')
        if player:
            player.change_gadget('NONE')


class Water(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.width = width
        self.height = height

        self.group = 'water'
        self.order = 3

    def render(self):
        peachy.graphics.set_color(0, 0, 255, 200)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        player = self.collides_name('player')
        if player:
            player.change_gadget('NONE')
