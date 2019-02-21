import peachy
import peachy.geo


class Button(peachy.Entity, peachy.geo.Rect):

    WAIT_TIME = 5 * 60

    def __init__(self, x, y, on_press):
        super(peachy.Entity).__init__()
        super(peachy.geo.Rect).__init__(16, 16)
        self.group = 'interact button'

        self.sprite = peachy.graphics.splice(
            peachy.fs.get_image('assets/img/button.png'), 8, 8)

        self.on_press = on_press
        self.wait_timer = 0

    def press(self):
        if self.wait_timer <= 0:
            exec(self.on_press)
            self.wait_timer = Button.WAIT_TIME

    def render(self):
        if self.wait_timer > 0:
            peachy.graphics.draw(self.sprite[0], self.x, self.y)
        else:
            peachy.graphics.draw(self.sprite[1], self.x, self.y)

    def update(self):
        if self.wait_timer > 0:
            self.wait_timer -= 1
