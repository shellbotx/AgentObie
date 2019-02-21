import peachy
import peachy.geo
from peachy import PC


class Checkpoint(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y):
        super(peachy.Entity).__init__()
        super(peachy.geo.Rect).__init__(x, y, 16, 16)

        self.group = 'checkpoint'

        self.order = 0

        self.checked = False
        self.old = False

    def render(self):
        # Placeholder rendering
        if self.checked:
            if self.old:
                peachy.graphics.set_color(255, 255, 0)
            else:
                peachy.graphics.set_color(0, 255, 0)
        else:
            peachy.graphics.set_color(255, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_text("+", self.x + 4, self.y + 4)

    def update(self):
        player = self.container.get_name('player')
        if player and self.collides(player, self.x, self.y):
            PC().world.set_checkpoint()
            self.checked = True
            self.old = False
