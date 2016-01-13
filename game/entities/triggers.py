import peachy
from peachy import PC

class Trigger(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'trigger'
        self.width = width
        self.height = height
        self.visible = False

class LevelChangeTrigger(Trigger):
    def __init__(self, x, y, width, height, link):
        Trigger.__init__(self, x, y, width, height)
        self.group = 'trigger level-change'
        self.link = link

class MessageTrigger(Trigger):

    def __init__(self, x, y, width, height, message):
        Trigger.__init__(self, x, y, width, height)
        self.group = 'trigger message'
        self.message = message

    def display(self):
        player = self.container.get_name('player')

        HEIGHT = 64
        y = PC.height - HEIGHT - 8

        if player.y + player.height > PC.height - HEIGHT:
            # y = PC.height - HEIGHT
            y = 8

        peachy.graphics.set_color(0, 30, 60)
        peachy.graphics.draw_rect(0, y, PC.width, HEIGHT)
        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_text(self.message, 8, y + 8)

class StageChangeTrigger(Trigger):

    def __init__(self, x, y, width, height, link):
        Trigger.__init__(self, x, y, width, height)
        self.group = 'trigger stage-change'
        self.link = link

