import peachy

class Rope(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'interact rope'

        self.width = width
        self.height = height

    def render(self):
        peachy.graphics.set_color(0, 255, 0)
        peachy.graphics.draw_line(self.x, self.y, self.x + self.width, self.y + self.height)
    #    peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
