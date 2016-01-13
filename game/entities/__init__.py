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


class Lift(peachy.Entity):

    SPEED = 0.25
    
    def __init__(self, start_x, start_y, end_x, end_y):
        peachy.Entity.__init__(self, start_x, start_y)

        self.dest1 = (start_x, start_y)
        self.dest2 = (end_x, end_y)

        self.target_x = start_x
        self.target_y = start_y

        self.width = 8
        self.height = 4
        self.solid = True

    def toggle(self):
        target = (self.target_x, self.target_y)

        dest = None
        if target != self.dest1:
            dest = self.dest1
        else:
            dest = self.dest2

        self.target_x, self.target_y = dest

    def render(self):
        peachy.graphics.set_color(255, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.x != self.target_x or self.y != self.target_y:
            temp_x = self.x
            temp_y = self.y
            
            if temp_y > self.target_y:
                temp_y -= Lift.SPEED
            elif temp_y < self.target_y:
                temp_y += Lift.SPEED

            delta_x = self.x - temp_x
            delta_y = self.y - temp_y

            passengers = self.collides_group('liftable', temp_x, temp_y)
            for passenger in passengers:
                passenger.x -= delta_x
                passenger.y -= delta_y

            self.x = temp_x
            self.y = temp_y


class HidingSpot(peachy.Entity):

    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self, x, y)
        self.group = 'hiding-spot interact'
        self.width = width
        self.height = height

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
