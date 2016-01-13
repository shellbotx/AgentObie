import peachy

class Solid(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'solid'
        self.width = width
        self.height = height
        self.solid = True
        self.visible = False

    def render(self):
        peachy.graphics.color = (255, 255, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
