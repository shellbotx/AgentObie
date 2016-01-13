import peachy

class Lever(peachy.Entity):
    
    def __init__(self, x, y, on_pull, lock):
        peachy.Entity.__init__(self, x, y)
        self.group = 'interact lever'
        self.width = 8
        self.height = 8
        self.pulled = False
        self.on_pull = on_pull
        self.lock = lock

    def render(self):
        if self.pulled:
            peachy.graphics.set_color(0, 255, 0)
        else:
            peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def pull(self):
        if not self.pulled:
            exec self.on_pull
            self.pulled = True
        elif not self.lock:
            exec self.on_pull
            self.pulled = False
