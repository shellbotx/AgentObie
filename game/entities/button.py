import peachy

class Button(peachy.Entity):

    WAIT_TIME = 5 * 60

    def __init__(self, x, y, on_press):
        super(Button, self).__init__(x, y)
        self.group = 'interact button'
        self.width = 16
        self.height = 16

        self.sprite = peachy.graphics.splice(
                peachy.fs.get_image('assets/img/button.png'), 8, 8)

        self.on_press = on_press
        self.wait_timer = 0
    
    def render(self):
        if self.wait_timer > 0: 
            peachy.graphics.draw(self.sprite[0], self.x, self.y)
        else:
            peachy.graphics.draw(self.sprite[1], self.x, self.y)

    def press(self):
        if self.wait_timer <= 0:
            exec self.on_press
            self.wait_timer = Button.WAIT_TIME

    def update(self):
        if self.wait_timer > 0:
            self.wait_timer -= 1
