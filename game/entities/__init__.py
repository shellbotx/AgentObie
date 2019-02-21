"""
The entities module includes all entity classes to allow for easy and quick
access from exterior modules. The entities module does not contain any classes
directly within its file, instead all classes are referenced from their own
seperate modules.
"""

from .blocks import PushBlock
from .bullet import Bullet
from .button import Button
from .checkpoint import Checkpoint
from .doors import Door, LockedDoor, RetractableDoor
from .dog import Dog
from .hazards import Pitfall, Spikes, TrashDropper
from .platforms import FallingPlatform
from .hiding_spot import HidingSpot
from .ladder import Ladder
from .lever import Lever
from .lifts import AutoLift, ManualLift
from .pickups import Key, GadgetPickup
from .pressure_plate import PressurePlate
from .player import Player
from .pulley import Pulley
from .rope import Rope
from .sensor import Sensor
from .soldier import Soldier
from .solid import Solid
from .triggers import ChangeLevelTrigger, ChangeStageTrigger, ShowMessageTrigger
from .turret import Turret
from .water import Water

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
            y = PC().canvas_height - HEIGHT

        peachy.graphics.set_color(0, 30, 60)
        peachy.graphics.draw_rect(0, y, PC().canvas_width, HEIGHT)
        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_message(self.message, 8, y + 8)

    def render(self):
        peachy.graphics.set_color(255, 0, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
