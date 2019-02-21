import peachy
import peachy.geo


class Door(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, link):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, 16, 12)
        self.group = 'interact door'

        self.link = link

    def render(self):
        peachy.graphics.set_color(255, 69, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)


class LockedDoor(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, width, height, tag):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.group = 'locked-door'
        self.solid = True
        self.tag = tag

    def render(self):
        peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)


class RetractableDoor(peachy.Entity, peachy.geo.Rect):
    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.group = 'retract'
        self.solid = True

    def render(self):
        peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
