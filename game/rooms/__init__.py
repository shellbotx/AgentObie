import logging
import os

import pygame
import peachy
import peachy.collision
import peachy.etc
import peachy.stage
from peachy import PC

from game import entities
from game.entities import Player
from game.utility import dxdy_from_string, string_escape


class AgentObieRoom(peachy.Room):
    """ Base class for all Agent Obie stages """

    def __init__(self, world):
        super().__init__(world)

        self.player = None

        self.stage_data = None
        self.previous_stage = ''
        self.foreground_layers = []
        self.background_layers = []

        self.camera = peachy.etc.Camera(320, 240)
        self.camera.min_x = 0
        self.camera.min_y = 0
        self.camera.max_x = 0
        self.camera.max_y = 0

        self.unlocked_doors = []

        self.particles = []

        self.starting_gadget = ''

        self.paused = False
        # The name that shows up in the pause menu
        self.pause_menu_name = 'AREA UNKNOWN'

    def add_particles(self, particles):
        if isinstance(particles, list):
            self.particles += particles
        else:
            self.particles.append(particles)

    def exit(self):
        if self.stage_data:
            self.stage_data.clear()
        self.clear()
        self.world = None
        del self.stage_data
        del self.player
        del self.foreground_layers
        del self.background_layers

    def load_tmx(self, path, _reload=False, to_check=False):
        stage_data = None
        previous_stage = ''

        if _reload:
            stage_data = self.stage_data
            previous_stage = self.previous_stage

        else:
            stage_data = peachy.stage.load_tiled_tmx(path)
            stage_data.name = os.path.basename(stage_data.filename)[:-4]
            logging.info('Loading: ' + stage_data.name)

            if self.stage_data:
                previous_stage = os.path.basename(self.stage_data.filename)

        if self.player is None:
            self.player = Player(0, 0)

        self.clear()

        for object_group in stage_data.objectgroups:
            if object_group.name == 'SOLID':
                for OBJ in object_group:
                    solid = entities.Solid(OBJ.x, OBJ.y, OBJ.width, OBJ.height)
                    if 'NAME' in OBJ.properties:
                        solid.name = OBJ.properties['NAME']
                    self.add(solid)
            else:
                for OBJ in object_group:
                    obj = self._parse_OBJ(OBJ, stage_data, previous_stage)

                    if obj is not None:
                        if 'NAME' in OBJ.properties:
                            obj.name = OBJ.properties['NAME']
                        if to_check and obj.member_of('checkpoint'):
                            self.player.x = obj.x
                            self.player.y = obj.y
                        self.add(obj)

        # Add player last so they are on the top of the render queue
        self.add(self.player)
        if self.player.state == Player.STATE_CLIMBING:
            try:
                ladder = peachy.collision.collides_group(
                    self, 'rope', self.player)[0]
                vertical = True
                if ladder.height == 0:
                    vertical = False
                self.player.change_state(Player.STATE_CLIMBING,
                                         handle=ladder, vertical=vertical)
            except IndexError:
                self.player.change_state(Player.STATE_STANDARD)
        self.sort()

        # Split stage layers
        self.foreground_layers = []
        self.background_layers = []
        for layer in stage_data.layers:
            if layer.layer_type is not 'tile':
                continue

            # Render layer tiles to static image
            layer_size = (layer.width * stage_data.tilewidth,
                          layer.height * stage_data.tileheight)
            layer_image = peachy.graphics.Surface(
                layer_size,
                flags=pygame.locals.HWSURFACE | pygame.locals.SRCALPHA)

            peachy.graphics.push_context(layer_image)
            for x, y, image in layer.tiles():
                if image is not None:
                    x *= stage_data.tilewidth
                    y *= stage_data.tileheight
                    peachy.graphics.draw(image, x, y)
            peachy.graphics.pop_context()

            layer_type = layer.name[:10]
            if layer_type == 'FOREGROUND' or layer_type[:2] == 'FG':
                # self.foreground_layers.append(layer)
                self.foreground_layers.append(layer_image)
            elif layer_type == 'BACKGROUND' or layer_type[:2] == 'BG':
                self.background_layers.append(layer_image)

        # Initialize camera
        self.camera.max_x = (stage_data.width * stage_data.tilewidth) \
            - self.camera.width
        self.camera.max_y = (stage_data.height * stage_data.tileheight) \
            - self.camera.height

        # Finalize
        if not _reload:
            if self.stage_data:
                self.previous_stage = os.path.basename(self.stage_data.filename)
            self.stage_data = stage_data
            self.starting_gadget = self.player.gadget.name

    def pause(self):
        self.pause_animations()
        self.paused = True

    def pause_animations(self):
        for e in self.entities:
            try:
                e.sprite.pause()
            except AttributeError:
                pass

    def resume(self):
        self.resume_animations()
        self.paused = False

    def resume_animations(self):
        for e in self.entities:
            try:
                e.sprite.resume()
            except AttributeError:
                pass

    def reload(self):
        self.player.change_state(Player.STATE_STANDARD)
        path = os.path.basename(self.stage_data.filename)
        self.load_tmx(path, True)

    def render(self):
        self.camera.snap_to(self.player.x, self.player.y, True)
        self.camera.translate()

        for layer in self.background_layers:
            peachy.graphics.draw(layer, 0, 0)
            # peachy.stage.render_layer(self.stage_data, layer)

        self.sort()
        super().render()

        for particle in self.particles:
            particle.render()

        for layer in self.foreground_layers:
            peachy.graphics.draw(layer, 0, 0)
            # peachy.stage.render_tiled_layer(self.stage_data, layer)

    def update(self):
        if peachy.utils.Key.pressed('r'):
            self.reload()

        if peachy.utils.Key.pressed('up'):
            doors = peachy.collision.collides_group(
                self, 'door', self.player)
            try:
                self.load_tmx('assets/' + doors[0].link)
                self.player.gadget.stop()
                return
            except IndexError:
                pass

            message_box = peachy.collision.collides_group(
                self, 'message-box', self.player)
            if message_box:
                # Cannot use GameWorld because of ImportError
                self.world.change_state('MESSAGE', message_box[0])
                return

        triggered = peachy.collision.collides_group(
            self, 'trigger', self.player)
        if triggered:
            trigger = triggered[0]
            if trigger.member_of('stage-change'):
                self.load_tmx('assets/' + trigger.link)

            elif trigger.member_of('level-change'):
                stage = stage_from_string(trigger.link)
                self.world.change_stage(stage)

            elif trigger.member_of('message'):
                self.world.change_state('message', trigger)

            return

        if self.player.state == Player.STATE_DEAD:
            self.world.change_state('game-over')
            return

        super().update()

        for particle in self.particles:
            particle.update()

    def _parse_OBJ(self, OBJ, stage, previous_stage):
        '''
        Loading stages is split into two functions to allow for easier level
        overrides
        '''

        # Handled in the loader now.
        # if OBJ.group == 'SOLID':
        #     return entities.Solid(OBJ.x, OBJ.y, OBJ.width, OBJ.height)
        if not OBJ.name:
            return None

        elif OBJ.name == 'DEBUG' and previous_stage == '':
            self.player.x = OBJ.x
            self.player.y = OBJ.y

        elif OBJ.name == 'BLOCK' or OBJ.name == 'PUSH_BLOCK':
            return entities.PushBlock(OBJ.x, OBJ.y)

        elif OBJ.name == 'BUTTON':
            on_press = string_escape(OBJ.properties['ON_PRESS'])
            return entities.Button(OBJ.x, OBJ.y, on_press)

        elif OBJ.name == 'CHANGE_LEVEL':
            link = OBJ.properties['LINK']
            return entities.ChangeLevelTrigger(OBJ.x, OBJ.y,
                                               OBJ.width, OBJ.height, link)

        elif OBJ.name == 'CHANGE_STAGE':
            link = OBJ.properties['LINK']

            continuous = False
            try:
                continuous = bool(OBJ.properties['CONTINUOUS'])
            except KeyError:
                pass

            if os.path.basename(link) == previous_stage:
                sx = OBJ.x
                sy = OBJ.y

                if continuous:
                    # TODO continous
                    continuous = False

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

            return entities.ChangeStageTrigger(OBJ.x, OBJ.y,
                                               OBJ.width, OBJ.height, link)

        elif OBJ.name == 'CHECKPOINT':
            checkpoint = entities.Checkpoint(OBJ.x, OBJ.y)
            if self.world.checkpoint and \
               self.world.checkpoint.stage == stage.filename:
                checkpoint.checked = True
                checkpoint.old = True
            return checkpoint

        elif OBJ.name == 'DOG':
            return entities.Dog(OBJ.x, OBJ.y)

        elif OBJ.name == 'DOOR':
            link = OBJ.properties['LINK']
            if os.path.basename(link) == previous_stage:
                self.player.x = OBJ.x
                self.player.y = OBJ.y
            return entities.Door(OBJ.x, OBJ.y, link)

        elif OBJ.name[:7] == 'GADGET_':
            gadget_type = OBJ.name[7:]
            return entities.GadgetPickup(OBJ.x, OBJ.y, gadget_type)

        elif OBJ.name == 'HIDING_SPOT':
            return entities.HidingSpot(OBJ.x, OBJ.y, OBJ.width, OBJ.height)

        elif OBJ.name == 'KEY':
            tag = OBJ.properties['TAG']
            if tag not in self.player.obtained_keys:
                return entities.Key(OBJ.x, OBJ.y, tag)

        elif OBJ.name == 'LADDER':
            return entities.Ladder(OBJ.x, OBJ.y, OBJ.height)

        elif OBJ.name == 'LIFT_C':
            nodes = []

            for point in OBJ.points:
                convert_point = peachy.geo.Point(
                    point[0] + OBJ.x,
                    point[1] + OBJ.y
                )
                nodes.append(convert_point)

            return entities.ManualLift(nodes, OBJ.width, OBJ.height)

        elif OBJ.name == 'LOCKED_DOOR':
            tag = OBJ.properties['TAG']
            if tag not in self.unlocked_doors:
                return entities.LockedDoor(OBJ.x, OBJ.y, OBJ.width, OBJ.height,
                                           tag)

        elif OBJ.name == 'LEVER':
            on_pull = ''
            lock = False

            try:
                on_pull = string_escape(OBJ.properties['ON_PULL'])
            except KeyError:
                logging.warning('[WARN] no pull operation found for lever')
                pass
            try:
                lock = OBJ.properties['LOCK']
            except KeyError:
                pass

            return entities.Lever(OBJ.x, OBJ.y, on_pull, lock)

        elif OBJ.name == 'MESSAGE_BOX':
            message = OBJ.properties['MESSAGE']
            return entities.MessageBox(OBJ.x, OBJ.y, message)

        elif OBJ.name == 'PITFALL':
            return entities.Pitfall(OBJ.x, OBJ.y, OBJ.width, OBJ.height)

        elif OBJ.name == 'PRESSURE_PLATE':
            on_press = ''
            on_release = ''
            down = ''

            try:
                on_press = string_escape(OBJ.properties['ON_PRESS'])
            except KeyError:
                pass
            try:
                on_release = string_escape(OBJ.properties['ON_RELEASE'])
            except KeyError:
                pass
            try:
                down = string_escape(OBJ.properties['DOWN'])
            except KeyError:
                pass

            return entities.PressurePlate(OBJ.x, OBJ.y, OBJ.width,
                                          on_press, on_release, down)

        elif OBJ.name == 'RETRACT':
            return entities.RetractableDoor(OBJ.x, OBJ.y, OBJ.width, OBJ.height)

        elif OBJ.name == 'ROPE':
            on_pull = ''
            on_release = ''
            down = ''

            try:
                on_pull = string_escape(OBJ.properties['ON_PULL'])
            except KeyError:
                pass
            try:
                on_release = string_escape(OBJ.properties['ON_RELEASE'])
            except KeyError:
                pass
            try:
                down = string_escape(OBJ.properties['DOWN'])
            except KeyError:
                pass

            return entities.Rope(OBJ.x, OBJ.y, OBJ.width, OBJ.height,
                                 on_pull, on_release, down)

        elif OBJ.name == 'SENSOR':
            gun = OBJ.properties['GUN']
            return entities.Sensor(OBJ.x, OBJ.y, OBJ.width, OBJ.height, gun)

        elif OBJ.name == 'SHOW_MESSAGE':
            message = OBJ.properties['MESSAGE']
            return entities.ShowMessageTrigger(OBJ.x, OBJ.y,
                                               OBJ.width, OBJ.height, message)

        elif OBJ.name == 'SOLDIER':
            stationary = False
            try:
                stationary = bool(OBJ.properties['STATIONARY'])
            except KeyError:
                pass

            soldier = entities.Soldier(OBJ.x, OBJ.y, stationary)

            try:
                facing = OBJ.properties['FACING']
                if facing == 'LEFT':
                    soldier.facing_x = -1
                elif facing == 'RIGHT':
                    soldier.facing_x = 1
            except KeyError:
                pass
            return soldier

        elif OBJ.name == 'SPIKES':
            return entities.Spikes(OBJ.x, OBJ.y, OBJ.width)

        elif OBJ.name == 'TURRET':
            direction = OBJ.properties['DIRECTION']
            dx, dy = dxdy_from_string(direction)
            return entities.Turret(OBJ.x, OBJ.y, dx, dy)

        elif OBJ.name == 'TRASH_DROPPER':
            return entities.TrashDropper(OBJ.x, OBJ.y, OBJ.width)

        elif OBJ.name == 'WATER':
            return entities.Water(OBJ.x, OBJ.y, OBJ.width, OBJ.height)


from .pier import Pier
from .sewer import Sewer


def stage_from_string(name):
    name = name.lower()
    if name == 'pier':
        return Pier(PC().get_world('game'))
    elif name == 'sewer':
        return Sewer(PC().get_world('game'))
    else:
        logging.warning('STAGE NOT FOUND %s' % (name))
