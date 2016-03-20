import os

import peachy
from peachy import DEBUG, PC, Scene
from peachy.utils import Point

from game.entities import *

class AgentObieScene(Scene):

    def __init__(self, world):
        super(AgentObieScene, self).__init__(world)

        self.player = None
        self.stage = None
        self.previous_stage = ''
        self.foreground_layers = []
        self.background_layers = []

        self.camera = peachy.utils.Camera(320, 240)
        self.camera.max_width = 320
        self.camera.max_height = 240

        self.unlocked_doors = []

    def draw_HUD(self):
        peachy.graphics.set_color(255, 255, 255)

        # Draw keys
        peachy.graphics.draw_text("KEYS: {0}".format(self.player.key_count), 0, 12)

        # Draw gadget detail
        if self.player.gadget.name == 'INVS':
            peachy.graphics.draw_text('INVS', 0, 24)
        else:
            peachy.graphics.draw_text('NONE', 0, 24)
        
        # Draw gadget timer
        time = str(round(float(self.player.gadget.timer) / 60.0, 1))
        x = (self.player.x + self.player.width + 4) * 2
        y = (self.player.y + 4) * 2
        
        if self.player.gadget.state == 0:
            peachy.graphics.draw_text(time, x, y)
        elif self.player.gadget.state == 2:
            peachy.graphics.set_color(255, 255, 0)
            peachy.graphics.draw_text(time, x, y)

    def exit(self):
        if self.stage:
            self.stage.clear()
        self.clear()
        self.world = None
        del self.stage
        del self.player
        del self.foreground_layers
        del self.background_layers

    def load_tmx(self, path):
        stage = peachy.utils.Stage.load_tiled(path)
        stage.name = os.path.basename(stage.path)[:-4]

        previous_stage = ''
        if self.stage:
            previous_stage = os.path.basename(self.stage.path)

        if self.player is None:
            self.player = Player(0, 0)
        
        self.clear()

        for OBJ in stage.objects:
            obj = self.load_stage_OBJ(OBJ, stage, previous_stage)

            if obj is not None:
                if 'NAME' in OBJ.properties:
                    obj.name = OBJ.properties['NAME']
                self.add(obj)

        # Add player last so they are on the top of the render queue
        self.add(self.player)
        if self.player.state == Player.STATE_CLIMBING:
            try:
                ladder = self.player.collides_group('rope')[0]
                vertical = True
                if ladder.height == 0:
                    vertical = False
                self.player.change_state(Player.STATE_CLIMBING, 
                    handle=ladder, vertical=vertical)
            except IndexError:
                self.player.change_state(Player.STATE_STANDARD)

        # TODO sort based on z-level

        self.foreground_layers = []
        self.background_layers = []
        for layer in stage.layers:
            layer_type = layer.name[:10]
            if layer_type == 'FOREGROUND' or layer_type[:2] == 'FG':
                self.foreground_layers.append(layer)
            elif layer_type == 'BACKGROUND' or layer_type[:2] == 'BG':
                self.background_layers.append(layer)

        self.camera.max_width = stage.width
        self.camera.max_height = stage.height

        self.previous_stage = self.stage
        self.stage = stage

    def load_stage_OBJ(self, OBJ, stage, previous_stage):
        '''
        Loading stages is split into two functions to allow for easier level
        overrides
        '''

        if OBJ.group == 'SOLID':
            return Solid(OBJ.x, OBJ.y, OBJ.w, OBJ.h)

        elif OBJ.name == 'DEBUG' and previous_stage == '':
            self.player.x = OBJ.x
            self.player.y = OBJ.y

        elif OBJ.name == 'BLOCK' or \
             OBJ.name == 'PUSH_BLOCK':
            return PushBlock(OBJ.x, OBJ.y)

        elif OBJ.name == 'BUTTON':
            on_press = OBJ.properties['ON_PRESS']
            return Button(OBJ.x, OBJ.y, on_press)

        elif OBJ.name == 'CHANGE_LEVEL':
            link = OBJ.properties['LINK']
            return ChangeLevelTrigger(OBJ.x, OBJ.y, OBJ.w, OBJ.h, link)

        elif OBJ.name == 'CHANGE_STAGE':
            link = OBJ.properties['LINK']

            continous = False
            try:
                continuous = bool(OBJ.properties['CONTINUOUS'])
            except KeyError:
                pass

            if os.path.basename(link) == previous_stage:
                sx = OBJ.x
                sy = OBJ.y
                # TODO if continuous:

                if OBJ.x < 0:
                    sx = 0
                elif OBJ.x >= stage.width:
                    sx = stage.width - Player.WIDTH
                if OBJ.y < 0:
                    sy = 0
                elif OBJ.y >= stage.height:
                    sy = stage.height - Player.HEIGHT_STANDARD

                self.player.x = sx
                self.player.y = sy

            return ChangeStageTrigger(OBJ.x, OBJ.y, OBJ.w, OBJ.h, link)

        elif OBJ.name == 'DOOR':
            link = OBJ.properties['LINK']
            if os.path.basename(link) == previous_stage:
                self.player.x = OBJ.x
                self.player.y = OBJ.y
            return Door(OBJ.x, OBJ.y, link)

        elif OBJ.name == 'GADGET_INVISIBLE' or \
             OBJ.name == 'GADGET_STUN' or \
             OBJ.name == 'GADGET_TIME':
            gadget_type = OBJ.name[7:]
            return GadgetPickup(OBJ.x, OBJ.y, gadget_type)

        elif OBJ.name == 'HIDING_SPOT':
            return HidingSpot(OBJ.x, OBJ.y, OBJ.w, OBJ.h)

        elif OBJ.name == 'KEY':
            tag = OBJ.properties['TAG']
            if tag not in self.player.obtained_keys:
                return Key(OBJ.x, OBJ.y, tag)

        elif OBJ.name == 'LIFT_C':
            nodes = []

            for point in OBJ.polygon_points:
                point.x += OBJ.x 
                point.y += OBJ.y
                nodes.append(point)

            return ManualLift(nodes, OBJ.w, OBJ.h)

        elif OBJ.name == 'LOCKED_DOOR':
            tag = OBJ.properties['TAG']
            if tag not in self.unlocked_doors:
                return LockedDoor(OBJ.x, OBJ.y, OBJ.w, OBJ.h, tag)

        elif OBJ.name == 'LEVER':
            on_pull = ''
            lock = False

            try:
                on_pull = OBJ.properties['ON_PULL']
            except KeyError:
                DEBUG('[WARN] no pull operation found for lever')
                pass
            try:
                lock = OBJ.properties['LOCK']
            except KeyError:
                pass

            return Lever(OBJ.x, OBJ.y, on_pull, lock)

        elif OBJ.name == 'MESSAGE_BOX':
            message = OBJ.properties['MESSAGE']
            return MessageBox(OBJ.x, OBJ.y, message)

        elif OBJ.name == 'RETRACT':
            return RetractableDoor(OBJ.x, OBJ.y, OBJ.w, OBJ.h)
        elif OBJ.name == 'ROPE' or OBJ.name == 'LADDER':
            return Rope(OBJ.x, OBJ.y, OBJ.w, OBJ.h)

        elif OBJ.name == 'SHOW_MESSAGE':
            message = OBJ.properties['MESSAGE']
            return ShowMessageTrigger(OBJ.x, OBJ.y, OBJ.w, OBJ.h, message)

        elif OBJ.name == 'SOLDIER':
            stationary = False
            try:
                stationary = bool(OBJ.properties['STATIONARY'])
            except KeyError:
                pass
        
            soldier = Soldier(OBJ.x, OBJ.y, stationary)

            try:
                facing = OBJ.properties['FACING']
                if facing == 'LEFT':
                    soldier.facing_x = -1
                elif facing == 'RIGHT':
                    soldier.facing_x = 1
            except KeyError:
                pass
            return soldier

    def reload_stage(self):
        self.player.change_state(Player.STATE_STANDARD)
        path = self.stage.path
        self.stage = self.previous_stage
        self.load_tmx(path)
    
    def update(self):
        if peachy.utils.Input.pressed('r'):
            self.reload_stage()

        if peachy.utils.Input.pressed('up'):
            doors = self.player.collides_group('door')
            try:
                self.load_tmx('assets/' + doors[0].link)
                return
            except IndexError:
                pass

            message_box = self.player.collides_group('message-box')
            if message_box:
                # Cannot use GameWorld because of ImportError
                self.world.state = 'message'  
                self.world.message = message_box[0]
                return
        
        triggered = self.player.collides_group('trigger')
        if triggered:
            trigger = triggered[0]
            if trigger.member_of('stage-change'):
                self.load_tmx('assets/' + trigger.link)
            elif trigger.member_of('level-change'):
                scene = scene_from_string(trigger.link)
                self.world.change_scene(scene)
            elif trigger.member_of('message'):
                self.world.state = 'message'
                self.world.message = trigger
            return
        
        if self.player.state == Player.STATE_DEAD:
            self.world.state = 'game-over'
            return

        super().update()
    
    def render(self):
        self.camera.snap(self.player.x, self.player.y, True)
        self.camera.translate()
        
        for layer in self.background_layers:
            self.stage.render_layer(layer)

        super().render()

        for layer in self.foreground_layers:
            self.stage.render_layer(layer)

from .pier import PierScene
from .sewer import SewerScene
from .tests import *

def scene_from_string(name):
    name = name.lower()
    if name == 'pier':
        return PierScene
    elif name == 'sewer':
        return SewerScene
    else:
        DEBUG('SCENE NOT FOUND {0}'.format(name))
