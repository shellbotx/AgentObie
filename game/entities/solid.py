import peachy

class Solid(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'solid'
        self.width = width
        self.height = height
        self.solid = True
        self.visible = False
        
        self.segments = []
        self.refresh_segments()

    def render(self):
        peachy.graphics.color = (255, 255, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def refresh_segments(self):
        self.segments = [
            [self.x, self.y, self.width, 0], 
            [self.x + self.width, self.y, 0, self.height], 
            [self.x + self.width, self.y + self.height, -self.width, 0], 
            [self.x, self.y + self.height, 0, -self.height]
        ]
