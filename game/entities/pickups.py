import peachy

class Key(peachy.Entity):
    
    def __init__(self, x, y, link):
        peachy.Entity.__init__(self, x, y)
        self.group = 'pickup key'
        self.width = 8
        self.height = 8
        self.link = link

    def render(self):
        peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

class GadgetPickup(peachy.Entity):
    def __init__(self, x, y, gadget):
        peachy.Entity.__init__(self, x, y)
        self.group = 'pickup gadget'
        self.gadget = gadget
        self.width = 8
        self.height = 16

    def render(self):
        if self.gadget == 'TIME':
            peachy.graphics.set_color(255, 0, 255)
        elif self.gadget == 'STUN':
            peachy.graphics.set_color(255, 255, 0)
        elif self.gadget == 'INVISIBLE':
            peachy.graphics.set_color(0, 255, 255)

        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
