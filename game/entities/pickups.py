import peachy
import peachy.geo


class Key(peachy.Entity):

    def __init__(self, x, y, tag):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, 8, 8)
        self.group = 'pickup key'
        self.tag = tag
        self.sprite = peachy.fs.get_image('assets/img/key.png')
        self.float = peachy.utils.Counter(0.5, 1.5, True, 0.005)

    def render(self):
        self.float.tick()
        peachy.graphics.draw(self.sprite, self.x, self.y - self.float.current)


class GadgetPickup(peachy.Entity):
    def __init__(self, x, y, gadget):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, 8, 8)
        self.group = 'pickup gadget'
        self.gadget = gadget

    def render(self):
        if self.gadget == 'TIME':
            peachy.graphics.set_color(255, 0, 255)
        elif self.gadget == 'STUN':
            peachy.graphics.set_color(255, 255, 0)
        elif self.gadget == 'INVISIBLE':
            peachy.graphics.set_color(0, 255, 255)
        elif self.gadget == 'DUPLICATE':
            peachy.graphics.set_color(0, 255, 0)

        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
