import peachy
import peachy.geo


class Pitfall(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.width = width
        self.height = height
        self.group = 'hazard pitfall'
        self.visible = False

    def update(self):
        player = self.collides_name('player')
        if player:
            player.kill(self)


class Spikes(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, width):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, 16)
        self.group = 'hazard spikes'

    def render(self):
        peachy.graphics.set_color(196, 196, 196)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        player = self.collides_name('player')
        if player:
            player.kill(self)


class TrashDropper(peachy.Entity, peachy.geo.Rect):

    COOLDOWN = 180

    def __init__(self, x, y, width):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, 8)
        self.group = 'hazard trash'
        self.timer = TrashDropper.COOLDOWN

    def render(self):
        peachy.graphics.set_color(125, 125, 125)
        peachy.graphics.draw_entity_rect(self)

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            tx = self.x
            while tx < self.x + self.width:
                self.container.add(Trash(tx, self.y, 8))
                tx += 8
            self.timer = TrashDropper.COOLDOWN


class Trash(peachy.Entity, peachy.geo.Rect):

    SPEED = 4

    def __init__(self, x, y, width):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, 8)

    def render(self):
        peachy.graphics.set_color(255, 0, 0)
        peachy.graphics.draw_entity_rect(self)

    def update(self):
        self.y += Trash.SPEED
        player = self.collides_name('player')
        if player:
            player.kill(self)
        if self.collides_solid():
            self.destroy()
