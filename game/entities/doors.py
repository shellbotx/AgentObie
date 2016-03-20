import peachy

class Door(peachy.Entity):

    def __init__(self, x, y, link):
        peachy.Entity.__init__(self, x, y)
        self.group = 'interact door'
        self.width = 16
        self.height = 12

        self.link = link

    def render(self):
        peachy.graphics.set_color(255, 69, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)


class LockedDoor(peachy.Entity):
    
    def __init__(self, x, y, width, height, tag):
        peachy.Entity.__init__(self, x, y)
        self.group = 'locked-door'
        self.solid = True
        self.width = width
        self.height = height
        self.tag = tag

    def render(self):
        peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)


class RetractableDoor(peachy.Entity):
    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'retract'
        self.solid = True
        self.width = width
        self.height = height

    def render(self):
        peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
