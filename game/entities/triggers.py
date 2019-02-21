import peachy
import peachy.geo
from peachy import PC


class Trigger(peachy.Entity, peachy.geo.Rect):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.group = 'trigger'
        self.width = width
        self.height = height
        self.visible = False


class ChangeLevelTrigger(Trigger):

    def __init__(self, x, y, width, height, link):
        super().__init__(x, y, width, height)
        self.group = 'trigger level-change'
        self.link = link


class ChangeStageTrigger(Trigger):

    def __init__(self, x, y, width, height, link):
        super().__init__(x, y, width, height)
        self.group = 'trigger stage-change'
        self.link = link


class ShowMessageTrigger(Trigger):

    def __init__(self, x, y, width, height, message):
        super().__init__(x, y, width, height)
        self.group = 'trigger message'
        self.message = message

    def display(self):
        player = self.container.get_name('player')

        HEIGHT = 64
        y = PC().canvas_height - HEIGHT - 8

        if player.y + player.height > PC().canvas_height - HEIGHT:
            # y = PC().canvas_height - HEIGHT
            y = 8

        peachy.graphics.set_color(0, 30, 60)
        peachy.graphics.draw_rect(0, y, PC().canvas_width, HEIGHT)
        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_text(self.message, 8, y + 8)
