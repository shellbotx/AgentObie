""" 
The entities module includes all entity classes to allow for easy and quick
access from exterior modules. The entities module does not contain any classes
directly within its file, instead all classes are referenced from their own
seperate modules.
"""

from blocks import PushBlock
from button import Button
from doors import Door, LockedDoor, RetractableDoor
from hiding_spot import HidingSpot
from lever import Lever
from lifts import AutoLift, ManualLift
from pickups import Key, GadgetPickup
from player import Player
from rope import Rope
from soldier import Soldier
from solid import Solid
from triggers import ChangeLevelTrigger, ChangeStageTrigger, ShowMessageTrigger

import peachy
from peachy import PC

class MessageBox(peachy.Entity):
    # TODO move this class elsewhere
    
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
