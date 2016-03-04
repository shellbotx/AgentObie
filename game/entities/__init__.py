import peachy
from peachy import PC

from player import Player
from solid import Solid
from rope import Rope
from soldier import Soldier
from blocks import PushBlock
from lever import Lever
from doors import Door, LockedDoor, RetractableDoor
from pickups import Key, GadgetPickup
from triggers import *
from lifts import *


class Button(peachy.Entity):

    WAIT_TIME = 5 * 60

    def __init__(self, x, y, on_press):
        super(Button, self).__init__(x, y)
        self.group = 'interact button'
        self.width = 16
        self.height = 16

        self.sprite = peachy.utils.splice_image('assets/img/button.png', 8, 8)

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


class HidingSpot(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'hiding-spot interact'
        self.width = width
        self.height = height
        self.visible = False

    def render(self):
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)


class MessageBox(peachy.Entity):
    
    def __init__(self, x, y, message):
        peachy.Entity.__init__(self, x, y)
        self.group = 'message-box interact'
        self.width = 8
        self.height = 8
        self.message = message
        # TODO split multiple pages of messages

    def advance(self):
        return

    def display(self):
        player = self.container.get_name('player')

        HEIGHT = 64
        y = 0

        if player.y + player.height < HEIGHT:
            y = PC.height - HEIGHT

        peachy.graphics.set_color(0, 30, 60)
        peachy.graphics.draw_rect(0, y, PC.width, HEIGHT)
        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_text(self.message, 8, y + 8)

    def render(self):
        peachy.graphics.set_color(255, 0, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
