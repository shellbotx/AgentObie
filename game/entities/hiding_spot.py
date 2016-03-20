import peachy

class HidingSpot(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'hiding-spot interact'
        self.width = width
        self.height = height
        self.visible = False

    def render(self):
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
