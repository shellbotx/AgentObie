import os

import peachy
from peachy import PC

import entities
from entities import *
import utility

class Level(object):
    '''
    SEWER_01
    SEWER_02
    SEWER_03
    SEWER_04
    SEWER_05
    '''

    def __init__(self, world):
        self.world = world
        self.player = None
        self.stage = None
        self.foreground_layers = []
        self.background_layers = []

        self.camera = peachy.utils.Camera(320, 240)

    def startup(self):
        return
    
    def exit(self):
        self.stage.clear()
        self.world = None
        del self.stage
        del self.player
        del self.foreground_layers
        del self.background_layers

    def load_stage(self, path):
        stage = peachy.utils.Stage.load_tiled(path)
        previous_stage = ''

        stage.name = os.path.basename(stage.path)[:-4]

        if self.stage:
            previous_stage = os.path.basename(self.stage.path)
        if self.player is None:
            self.player = Player(0, 0)
        
        self.world.entities.clear()

        for OBJ in stage.objects:
            obj = self.load_stage_OBJ(OBJ, stage, previous_stage)

            if obj is not None:
                if 'NAME' in OBJ.properties:
                    obj.name = OBJ.properties['NAME']
                self.world.entities.add(obj)

        # Add player last so they are on the top of the render queue
        self.world.entities.add(self.player)

        # TODO sort based on z-level

        self.foreground_layers = []
        self.background_layers = []
        for layer in stage.layers:
            layer_type = layer.name[:10]
            if layer_type == 'FOREGROUND':
                self.foreground_layers.append(layer)
            elif layer_type == 'BACKGROUND':
                self.background_layers.append(layer)

        self.camera.max_width = stage.width
        self.camera.max_height = stage.height

        self.stage = stage

    def load_stage_OBJ(self, OBJ, stage, previous_stage):
        '''
        Loading stages is split into two functions to allow for easier level
        overrides
        '''

        if OBJ.group == 'SOLID':
            return Solid(OBJ.x, OBJ.y, OBJ.w, OBJ.h)

        elif OBJ.name == 'CHANGE_LEVEL':
            link = OBJ.properties['LINK']
            return LevelChangeTrigger(OBJ.x, OBJ.y, OBJ.w, OBJ.h, link)

        elif OBJ.name == 'CHANGE_STAGE':
            link = OBJ.properties['LINK']

            continous = False
            try:
                continuous = bool(OBJ.properties['CONTINUOUS'])
            except KeyError:
                pass

            if link == previous_stage:
                sx = OBJ.x
                sy = OBJ.y
                # TODO if continuous:

                if OBJ.x < 0:
                    sx = 0
                elif OBJ.x >= stage.width:
                    sx = stage.width - Player.WIDTH
                if OBJ.y < 0:
                    sy = 0
                elif OBJ.y > stage.height:
                    sy = stage.height - Player.HEIGHT
                self.player.x = sx
                self.player.y = sy

            return StageChangeTrigger(OBJ.x, OBJ.y, OBJ.w, OBJ.h, link)
        elif OBJ.name == 'DOOR':
            link = OBJ.properties['LINK']
            if link == previous_stage:
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
            link = OBJ.properties['LINK']
            return Key(OBJ.x, OBJ.y, link)
        elif OBJ.name == 'LOCKED_DOOR':
            link = OBJ.properties['LINK']
            return  LockedDoor(OBJ.x, OBJ.y, OBJ.w, OBJ.h, link)
        elif OBJ.name == 'LEVER':
            on_pull = ''
            lock = False

            try:
                on_pull = OBJ.properties['ON_PULL']
            except KeyError:
                pass
            try:
                lock = OBJ.properties['LOCK']
            except KeyError:
                pass

            return Lever(OBJ.x, OBJ.y, on_pull, lock)
        elif OBJ.name == 'BLOCK' or OBJ.name == 'PUSH_BLOCK':
            return PushBlock(OBJ.x, OBJ.y)
        elif OBJ.name == 'MESSAGE_BOX':
            message = OBJ.properties['MESSAGE']
            return MessageBox(OBJ.x, OBJ.y, message)
        elif OBJ.name == 'RETRACT':
            return RetractableDoor(OBJ.x, OBJ.y, OBJ.w, OBJ.h)
        elif OBJ.name == 'ROPE' or OBJ.name == 'LADDER':
            return Rope(OBJ.x, OBJ.y, OBJ.w, OBJ.h)
        elif OBJ.name == 'SHOW_MESSAGE':
            message = OBJ.properties['MESSAGE']
            return MessageTrigger(OBJ.x, OBJ.y, OBJ.w, OBJ.h, message)
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
    
    def update(self):
        if peachy.utils.Input.pressed('up'):
            doors = self.player.collides_group('door')
            try:
                self.load_stage('assets/' + doors[0].link)
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
                self.load_stage('assets/' + trigger.link)
            elif trigger.member_of('level-change'):
                self.world.change_level(trigger.link)
            elif trigger.member_of('message'):
                self.world.state = 'message'
                self.world.message = trigger
            return

        self.world.entities.update()
    
    def render(self):
        self.camera.snap(self.player.x, self.player.y, True)
        self.camera.translate()
        
        for layer in self.background_layers:
            self.stage.render_layer(layer)

        self.world.entities.render()

        for layer in self.foreground_layers:
            self.stage.render_layer(layer)


class Level01(Level):

    def __init__(self, world):
        Level.__init__(self, world)
        self.world = world

    def startup(self):
        self.player = Player(80, 200)
        self.load_stage('assets/pier_01.tmx')

    def load_stage_OBJ(self, OBJ, stage, previous_stage):
        if OBJ.name == 'CARGO_LIFT':
            # TODO load custom image for cargo lift
            start_x = OBJ.x
            start_y = OBJ.y

            movement = OBJ.polygon_points[1]
            end_x = OBJ.x + movement[0]
            end_y = OBJ.y + movement[1]

            lift = Lift(start_x, start_y, end_x, end_y)
            lift.width = 56
            lift.height = 32

            return lift
        else:
            return Level.load_stage_OBJ(self, OBJ, stage, previous_stage)
    
    def update(self):
        # print self.stage.name
        Level.update(self)


class Level02(Level):
    
    def __init__(self, world):
        Level.__init__(self, world)
        self.world = world

    def startup(self):
        self.player = Player(152, 0)
        self.load_stage('assets/sewer_01.tmx')
        

class TestLevel(Level):

    def __init__(self, world):
        Level.__init__(self, world)
        self.world = world

    def load_stage(self, path):
        Level.load_stage(self, path)
        for e in self.world.entities:
            if e.member_of('solid'):
                e.visible = True
        self.player.change_gadget('TIME')
        # self.world.entities.add(MessageBox(4, 184, 'TEST MESSAGE'))

    def render(self):
        peachy.graphics.set_color_hex('#000055')

        for x in xrange(-9, PC.width / 2, 16):
            peachy.graphics.draw_line(x, 0, x, PC.height / 2)
        for y in xrange(-8, PC.height / 2, 16):
            peachy.graphics.draw_line(0, y, PC.width, y)

        Level.render(self)
