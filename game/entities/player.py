import peachy
from peachy import graphics
from peachy.utils import Input
from game.utility import *

GRAVITY = 0.2
MAX_GRAVITY = 9

class Player(peachy.Entity):

    SPEED = 1
    SPEED_FAST = 1.5
    SPEED_SLOW = 0.5
    JUMP_FORCE = 3

    STATE_STANDARD = 'standard'
    STATE_CLIMBING = 'climb'
    STATE_CROUCHING = 'crouch'
    STATE_DEAD = 'dead'
    STATE_HIDDEN = 'hidden'
    STATE_LEDGEGRAB = 'ledge-grab'
    STATE_PUSHING = 'push'
    
    WIDTH = 8
    HEIGHT_STANDARD = 12
    HEIGHT_CROUCH = 8

    def __init__(self, x, y):
        super(Player, self).__init__(x, y)

        self.name = 'player'
        self.group = 'liftable opaque'
        self.width = Player.WIDTH
        self.height = Player.HEIGHT_STANDARD
        self.facing_x = 1

        self.state = Player.STATE_STANDARD
        self.state_args = {}

        self.sprite = graphics.SpriteMap(
            peachy.fs.get_image('PlayerSprite'), 16, 16)

        os=(4, 4)  # origin_standard
        oc=(4, 8)  # origin_crouch
        self.sprite.add('IDLE', [0], origin=os)
        self.sprite.add('RUN', [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 4, True, origin=os)
        self.sprite.add('JUMP', [19], origin=os)
        self.sprite.add('FALL', [1], origin=os)
        self.sprite.add('PUSH', [2], origin=os)
        self.sprite.add('CROUCH', [20], origin=oc)
        self.sprite.add('CRAWL', [20, 21, 22, 23, 24, 25], 5, True, origin=oc)
        self.sprite.add('HANG', [3], origin=(4, 0))
        self.sprite.add('INVISIBLE', [4], origin=os)
        self.sprite.add('HIDDEN', [5], origin=os)
        self.sprite.add('TODO', [9])

        self.sprite.play('IDLE')

        self.gadget = Gadget(self)
        self.invisible = False

        self.obtained_keys = []
        self.key_count = 0

    def change_gadget(self, gadget_name):
        if gadget_name == 'INVISIBLE':
            self.gadget = InvisibilityCloak(self)
        elif gadget_name == 'STUN':
            self.gadget = StunBomb(self)
        elif gadget_name == 'TIME':
            self.gadget = TimeDisruptor(self)

    def change_state(self, state, **kwargs):
        self.state_args = kwargs

        if self.gadget.name != InvisibilityCloak.NAME or self.gadget.state != Gadget.STATE_ACTIVE:
            self.invisible = False

        if state == Player.STATE_STANDARD:
            diff_height = self.height - Player.HEIGHT_STANDARD
            self.y += diff_height
            self.height = Player.HEIGHT_STANDARD

        elif state == Player.STATE_CLIMBING:
            handle = kwargs['handle']

            if kwargs['vertical']:
                self.x = handle.x - (handle.x % 8)
            else:
                self.y = handle.y

            self.velocity_x = 0
            self.velocity_y = 0

        elif state == Player.STATE_CROUCHING:
            diff_height = self.height - Player.HEIGHT_CROUCH
            self.y += diff_height
            self.velocity_y = 0
            self.height = Player.HEIGHT_CROUCH

        elif state == Player.STATE_DEAD:
            self.velocity_x = 0
            self.velocity_y = 0

        elif state == Player.STATE_HIDDEN:
            hiding_spot = kwargs['hiding_spot']
            self.invisible = True

            if self.x < hiding_spot.x:
                self.x = hiding_spot.x
            if self.x + self.width >= hiding_spot.x + hiding_spot.width:
                self.x = hiding_spot.x + hiding_spot.width - self.width

            self.velocity_x = 0
            self.velocity_y = 0

        elif state == Player.STATE_LEDGEGRAB:
            ledge = kwargs['ledge']
            self.y = ledge.y
            self.height = Player.HEIGHT_STANDARD
            self.velocity_x = 0
            self.velocity_y = 0

        self.state = state

    def kill(self, cause):
        if cause.member_of('soldier-bullet'):
            # play shot animation
            print('SHOT DEAD')
        self.change_state(Player.STATE_DEAD)

    def render(self):
        flip_x = self.facing_x == -1

        if self.invisible:
            if self.state == Player.STATE_HIDDEN:
                self.sprite.play('HIDDEN', flip_x)
            else:
                self.sprite.play('INVISIBLE', flip_x)
        elif self.state == Player.STATE_STANDARD:
            if self.velocity_y == 0 and not solid_below(self, self.x, self.y):
                self.sprite.play('JUMP', flip_x)
            elif self.velocity_y < 0:
                self.sprite.play('JUMP', flip_x)
            elif self.velocity_y > 0:
                self.sprite.play('FALL', flip_x)
            elif self.velocity_x != 0:
                self.sprite.play('RUN', flip_x)
            else:
                self.sprite.play('IDLE', flip_x)
        elif self.state == Player.STATE_CROUCHING:
            if self.velocity_x != 0:
                self.sprite.play('CRAWL', flip_x)
            else:
                self.sprite.play('CROUCH', flip_x) 
        elif self.state == Player.STATE_LEDGEGRAB:
            self.sprite.play('HANG', flip_x)
        elif self.state == Player.STATE_PUSHING:
            self.sprite.play('PUSH', flip_x)
        else:
            graphics.set_color(125, 125, 125)
            graphics.draw_rect(self.x, self.y, self.width, self.height)
            self.gadget.render()
            return
        if Input.down('g'):
            graphics.set_color(125, 125, 125)
            graphics.draw_rect(self.x, self.y, self.width, self.height)
            self.gadget.render()
            return

        self.sprite.render(self.x, self.y)
        self.gadget.render()

    def update(self):
        temp_x = self.x
        temp_y = self.y
        has_solid_below = solid_below(self, self.x, self.y)
        
        keydown_up = Input.down('up')
        keydown_down = Input.down('down')
        keydown_left = Input.down('left')
        keydown_right = Input.down('right')
        keydown_run = Input.down('lshift') or Input.down('rshift')
        keypressed_up = Input.pressed('up')
        keypressed_down = Input.pressed('down')
        keypressed_left = Input.pressed('left')
        keypressed_right = Input.pressed('right')
        keypressed_jump = Input.pressed('space')
        keypressed_gadget = Input.pressed('x')

        if self.state == Player.STATE_STANDARD:
            # Run/Walk
            if keydown_left == keydown_right:
                self.velocity_x = 0
            else:
                if keydown_left:
                    if keydown_run:
                        self.velocity_x = -Player.SPEED_FAST
                    else:
                        self.velocity_x = -Player.SPEED
                    self.facing_x = -1
                if keydown_right:
                    if keydown_run:
                        self.velocity_x = Player.SPEED_FAST
                    else:
                        self.velocity_x = Player.SPEED
                    self.facing_x = 1

                block = self.collides_group('block', temp_x + self.velocity_x, self.y)
                if len(block) == 1 and has_solid_below:
                    block = block[0]
                    block_temp_x = block.x + self.velocity_x

                    if not block.collides_solid(block_temp_x, block.y):
                        self.change_state(Player.STATE_PUSHING, block=block)
                        if self.x < block.x:
                            self.x = block.x - self.width
                        else:
                            self.x = block.x + block.width
                        return

            # Jump
            if keypressed_jump and has_solid_below:
               self.velocity_y = -Player.JUMP_FORCE

            # Wall Grab
            if self.velocity_y < 4 and self.velocity_y > 0:
                climb_wall = []
                if keydown_left:
                    climb_wall = solid_left(self, self.x, self.y)
                if keydown_right:
                    climb_wall = solid_right(self, self.x, self.y)

                ledge = None
                for wall in climb_wall:
                    if wall.y - self.y < 3 and not wall.member_of('block'):
                        if self.y <= wall.y:
                            ledge = wall
                        else:
                            ledge = None

                if ledge is not None:
                    test = Rect(self.x, ledge.y - Player.HEIGHT_CROUCH,
                                self.width, Player.HEIGHT_CROUCH)
                    test.container = self.container

                    if test.x + test.width <= ledge.x:
                        test.x = ledge.x
                    elif test.x >= ledge.x + ledge.width:
                        test.x = ledge.x + ledge.width - test.width
                    
                    if not test.collides_solid():
                        self.change_state(Player.STATE_LEDGEGRAB, ledge=ledge)
                        return

            # Interact
            if keydown_up:
                interactables = self.collides_group('interact')
                for interact in interactables:
                    if interact.member_of('rope'):
                        vertical = False
                        if interact.width == 0:
                            vertical = True
                        elif interact.height == 0:
                            vertical = False

                        self.change_state(Player.STATE_CLIMBING,
                                handle=interact, vertical=vertical)
                        return

                    elif keypressed_up:
                        if interact.member_of('door'):
                            if self.gadget.state == Gadget.STATE_ACTIVE:
                                self.gadget.cancel()
                            interact.enter()

                        elif interact.member_of('button'):
                            interact.press()

                        elif interact.member_of('lever'):
                            interact.pull()
                        
                        elif interact.member_of('hiding-spot'):
                            self.change_state(Player.STATE_HIDDEN, hiding_spot=interact)
                            return
                        
                        elif interact.member_of('message-box'):
                            interact.activate()
                            return

            # Pickup
            if keypressed_up:
                pickups = self.collides_group('pickup')
                for pickup in pickups:
                    if pickup.member_of('gadget'):
                        self.change_gadget(pickup.gadget)
                    elif pickup.member_of('key'):
                        self.obtained_keys.append(pickup.tag)
                        self.key_count += 1
                        pickup.destroy()

            # Gadget
            if keypressed_gadget:
                self.gadget.use()

            # Crouching
            if keypressed_down and has_solid_below:
                self.change_state(Player.STATE_CROUCHING)
                return

            # Gravity
            if self.velocity_y < MAX_GRAVITY:
                self.velocity_y += GRAVITY

        elif self.state == Player.STATE_CLIMBING:
            if keypressed_jump:
                self.velocity_y = -Player.JUMP_FORCE
                self.change_state(Player.STATE_STANDARD)
                return

            handle = self.state_args['handle']
            vertical = self.state_args['vertical']

            if vertical:
                if keydown_up == keydown_down:
                    self.velocity_y = 0
                else:
                    if keydown_up:
                        if self.y > handle.y:
                            self.velocity_y = -Player.SPEED_SLOW
                        else:
                            self.velocity_y = 0
                    if keydown_down:
                        if self.y + self.height < handle.y + handle.height:
                            self.velocity_y = Player.SPEED_SLOW
                        else:
                            self.velocity_y = 0
            else:
                if keypressed_down:
                    self.change_state(Player.STATE_STANDARD)
                    return

                if keydown_left == keydown_right:
                    self.velocity_x = 0
                else:
                    if keydown_left:
                        if self.x > handle.x:
                            self.velocity_x = -Player.SPEED_SLOW
                        else:
                            self.velocity_x = 0
                    if keydown_right:
                        if self.x + self.width < handle.x + handle.width:
                            self.velocity_x = Player.SPEED_SLOW
                        else:
                            self.velocity_x = 0

        elif self.state == Player.STATE_CROUCHING:
            if keydown_left == keydown_right:
                self.velocity_x = 0
            else:
                if keydown_left:
                    self.velocity_x = -Player.SPEED_SLOW
                    self.facing_x = -1
                if keydown_right:
                    self.velocity_x = Player.SPEED_SLOW
                    self.facing_x = 1

                # attempt to grab ledge when crawling off one
                tx = self.velocity_x + self.x
                if not solid_below(self, tx, self.y):
                    ledges = solid_below(self, self.x, self.y)
                    try:
                        ledge = ledges[0]

                        if self.velocity_x > 0:
                            test = Rect(ledge.x + ledge.width, ledge.y, 
                                        self.width, Player.HEIGHT_STANDARD)
                        else:
                            test = Rect(ledge.x - self.width, ledge.y,
                                        self.width, Player.HEIGHT_STANDARD)

                        test.container = self.container
                            
                        if not test.collides_solid():
                            self.x = test.x
                            self.change_state(Player.STATE_LEDGEGRAB, ledge=ledge)
                            return
                    except IndexError:
                        pass
            
            attempt_stand = False

            if keypressed_jump and has_solid_below:
                self.velocity_y = -Player.JUMP_FORCE
                attempt_stand = True
            if not keydown_down:
                attempt_stand = True

            if attempt_stand:
                self.height = Player.HEIGHT_STANDARD
                temp_y = self.y - abs(Player.HEIGHT_STANDARD - Player.HEIGHT_CROUCH)
                if self.collides_solid(self.x, temp_y):
                    self.height = Player.HEIGHT_CROUCH
                    temp_y = self.y
                    self.velocity_y = 0
                else:
                    self.state = Player.STATE_STANDARD
                    self.y = temp_y

            self.height = Player.HEIGHT_STANDARD
            if self.collides_solid(temp_x, temp_y):
                self.height = Player.HEIGHT_CROUCH
            else:
                self.state = Player.STATE_STANDARD

        elif self.state == Player.STATE_HIDDEN:
            if keypressed_up or keypressed_left or keypressed_right:
                self.change_state(Player.STATE_STANDARD)

        elif self.state == Player.STATE_LEDGEGRAB:

            # Climb up ledge
            if keypressed_up or keypressed_left or keypressed_right:
                ledges = None
                if keydown_up:
                    try: 
                        ledges = solid_left(self, self.x, self.y)
                        assert ledges[0].y == self.y
                    except (AssertionError, IndexError):
                        ledges = solid_right(self, self.x, self.y)
                elif keydown_left:
                    ledges = solid_left(self, self.x, self.y)
                elif keydown_right:
                    ledges = solid_right(self, self.x, self.y)

                try:
                    ledge = ledges[0]
                    assert ledge.y == self.y

                    test = Rect(self.x, ledge.y - Player.HEIGHT_CROUCH,
                                self.width, Player.HEIGHT_CROUCH)
                    test.container = self.container

                    if test.x + test.width <= ledge.x:
                        test.x = ledge.x
                    elif test.x >= ledge.x + ledge.width:
                        test.x = ledge.x + ledge.width - test.width

                    if not test.collides_solid():
                        self.change_state(Player.STATE_CROUCHING)
                        self.x = test.x
                        self.y = test.y
                        return
                except (AssertionError, IndexError):
                    pass

            # Let go of ledge
            if keypressed_left and not solid_left(self, self.x, self.y) or \
               keypressed_right and not solid_right(self, self.x, self.y) or \
               keypressed_down:
                self.state = Player.STATE_STANDARD
            if keypressed_jump:
                self.state = Player.STATE_STANDARD
                self.velocity_y = -Player.JUMP_FORCE

        elif self.state == Player.STATE_PUSHING:
            block = self.state_args['block']

            if self.x > block.x and keydown_left:
                self.velocity_x = -Player.SPEED_SLOW
            elif self.x < block.x and keydown_right:
                self.velocity_x = Player.SPEED_SLOW
            else:
                self.change_state(Player.STATE_STANDARD)
                return

            if keypressed_jump:
                self.velocity_y = -Player.JUMP_FORCE
                self.change_state(Player.STATE_STANDARD)
                return

            test_x = temp_x + self.velocity_x
            if not self.collides(block, test_x, self.y):
                self.change_state(Player.STATE_STANDARD)
                return

            block_temp_x = block.x + self.velocity_x
            if not block.collides_solid(block_temp_x, block.y):
                block.x = block_temp_x

        # ADVANCE
        temp_x += self.velocity_x
        temp_y += self.velocity_y

        # LOCKED DOOR
        lock = self.collides_group('locked-door', temp_x, temp_y)
        if lock:
            lock = lock[0]
            if self.key_count > 0:
                self.key_count -= 1
                self.container.unlocked_doors.append(lock.tag)
                lock.destroy()

        # FINALIZE
        c, self.x, self.y, self.velocity_x, self.velocity_y = \
            collision_resolution(self, temp_x, temp_y)

        self.gadget.update()


# GADGETS


class Gadget(object):

    STATE_ACTIVE = 0
    STATE_INACTIVE = 1
    STATE_COOLDOWN = 2

    def __init__(self, name):
        self.name = name
        self.timer = 0
        self.state = Gadget.STATE_INACTIVE

    def cancel(self):
        return

    def use(self):
        if self.state == Gadget.STATE_INACTIVE:
            self.state = Gadget.STATE_ACTIVE
            self.timer = 60 * 3


    def render(self):
        return

    def update(self):
        return


class StunBomb(Gadget):

    NAME = 'STUN'
    COOLDOWN = 60 * 2
    DURATION = 60 * 0.25
    MAX_RADIUS = 32

    def __init__(self, player):
        Gadget.__init__(self, StunBomb.CODE)
        self.radius = 0
        self.player = player

    def cancel(self):
        if self.state == Gadget.STATE_ACTIVE:
            self.state = Gadget.STATE_COOLDOWN
            self.timer = StunBomb.COOLDOWN

    def use(self):
        if self.state == Gadget.STATE_INACTIVE:
            self.state = Gadget.STATE_ACTIVE
            self.timer = StunBomb.DURATION
            self.x = self.player.x + self.player.width / 2
            self.y = self.player.y + self.player.height / 2

    def render(self):
        if self.state == Gadget.STATE_ACTIVE:
            peachy.graphics.set_color(255, 255, 0, 64)
            peachy.graphics.draw_circle(self.x - self.radius, self.y - self.radius, self.radius)

    def update(self):
        if self.timer > 0:
            self.timer -= 1

        if self.state == Gadget.STATE_ACTIVE:
            self.radius = StunBomb.MAX_RADIUS * float(float(StunBomb.DURATION - self.timer) / StunBomb.DURATION)
            self.radius = int(self.radius)

            # Attempt to stun enemies
            candidates = self.player.container.get_group('can-stun')
            for entity in candidates:
                if not entity.stunned and \
                   entity.collides_circle((self.x, self.y, self.radius)):
                    entity.GADGET_stun()

            if self.timer <= 0:
                self.state = Gadget.STATE_COOLDOWN
                self.timer = StunBomb.COOLDOWN

        elif self.state == Gadget.STATE_COOLDOWN:
            if self.timer <= 0:
                self.state = Gadget.STATE_INACTIVE
                self.timer = 0


class InvisibilityCloak(Gadget):

    NAME = 'INVS'
    COOLDOWN = 60 * 5
    DURATION = 60 * 3

    def __init__(self, player):
        Gadget.__init__(self, InvisibilityCloak.NAME)
        self.player = player

    def cancel(self):
        if self.state == Gadget.STATE_ACTIVE:
            self.state = Gadget.STATE_COOLDOWN
            self.timer = InvisibilityCloak.COOLDOWN

    def use(self):
        if self.state == Gadget.STATE_INACTIVE:
            self.state = Gadget.STATE_ACTIVE
            self.timer = InvisibilityCloak.DURATION
            self.player.invisible = True

    def render(self):
        if self.state == Gadget.STATE_ACTIVE:
            peachy.graphics.set_color(0, 255, 255, 32)
            peachy.graphics.draw_circle(self.player.x - (self.player.width / 2) - 8, 
                                        self.player.y - (self.player.height / 2) - 6, 16)

    def cancel(self):
        if self.state ==  Gadget.STATE_ACTIVE:
            self.state = Gadget.STATE_COOLDOWN
            self.timer = InvisibilityCloak.COOLDOWN
            self.player.invisible = False

    def update(self):
        if self.timer > 0:
            self.timer -= 1

        if self.state == Gadget.STATE_ACTIVE:
            if self.timer <= 0:
                self.cancel()
                # self.state = Gadget.STATE_COOLDOWN
                # self.timer = InvisibilityCloak.COOLDOWN
                # self.player.invisible = False

        elif self.state == Gadget.STATE_COOLDOWN:
            if self.timer <= 0:
                self.state = Gadget.STATE_INACTIVE
                self.timer = 0


class TimeDisruptor(Gadget):

    NAME = 'TIME'
    COOLDOWN = 60 * 2
    DURATION = 60 * 3
    RADIUS = 32

    def __init__(self, player):
        Gadget.__init__(self, TimeDisruptor.NAME)
        self.player = player

    def use(self):
        if self.state == Gadget.STATE_INACTIVE:
            self.state = Gadget.STATE_ACTIVE
            self.timer = TimeDisruptor.DURATION
            self.x = self.player.x + self.player.width / 2 - TimeDisruptor.RADIUS
            self.y = self.player.y + self.player.height / 2 - TimeDisruptor.RADIUS

    def render(self):
        if self.state == Gadget.STATE_ACTIVE:
            peachy.graphics.set_color(255, 0, 255, 64)
            peachy.graphics.draw_circle(self.x, self.y, TimeDisruptor.RADIUS)

    def update(self):
        if self.timer > 0:
            self.timer -= 1

        if self.state == Gadget.STATE_ACTIVE:
            # Attempt to slow or revert slow
            ents = self.player.container.get_group('can-slow')
            for entity in ents:
                if entity.collides_circle((self.x, self.y, TimeDisruptor.RADIUS)):
                    if not entity.slowed:
                        entity.GADGET_slow()
                elif entity.slowed:
                    entity.GADGET_revert()

            # Change state (ACTIVE -> COOLDOWN)
            # -> Go through each time manipulatable entity and make sure their
            # state has been reverted
            if self.timer <= 0:
                ents = self.player.container.get_group('can-slow')
                for entity in ents:
                    if entity.slowed:
                        entity.GADGET_revert()
                self.state = TimeDisruptor.STATE_COOLDOWN
                self.timer = TimeDisruptor.COOLDOWN

        elif self.state == Gadget.STATE_COOLDOWN:
            # Change state (COOLDOWN -> INACTIVE)
            if self.timer <= 0:
                self.state = TimeDisruptor.STATE_INACTIVE
                self.timer = 0

