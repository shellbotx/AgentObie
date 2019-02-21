import peachy
import peachy.geo
from peachy import graphics, PC
from peachy.collision import collides_solid, collides_group, rect_rect
from peachy.utils import Key
from game import config
from game.utility import collision_resolution, solid_below, solid_left, \
    solid_right
from . import gadgets


class Player(peachy.Entity, peachy.geo.Rect):

    SPEED = 0.75
    SPEED_FAST = 2.5
    SPEED_SLOW = 0.5
    JUMP_FORCE = 2.5

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
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(
            self, x, y, Player.WIDTH, Player.HEIGHT_STANDARD)

        self.name = 'player'
        self.group = 'player liftable'

        self.facing_x = 1
        self.velocity_x = 0
        self.velocity_y = 0

        self.state = Player.STATE_STANDARD
        self.state_args = {}

        self.sprite = PC().resources.get_resource_by_name('ObieSprite')
        self.sprite.play('IDLE')
        self.walking_sound = PC().resources.get_resource_by_name(
            'FootstepSound')

        self.gadget = gadgets.Gadget(self, '')
        self.invisible = False

        self.obtained_keys = []
        self.key_count = 0

        self.order = 1

    def change_gadget(self, gadget_name):
        self.gadget.stop()
        self.gadget = gadgets.from_name(gadget_name, self)

    def change_state(self, state, **kwargs):
        self.state_args = kwargs

        self.walking_sound.stop()

        if self.gadget.name != gadgets.InvisibilityCloak.NAME or \
           self.gadget.state != gadgets.Gadget.STATE_ACTIVE:
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
        # TODO play Player death animation
        if cause.member_of('bullet'):
            print('SHOT DEAD')
        elif cause.member_of('dog'):
            print('GOT BIT')
        elif cause.member_of('pitfall'):
            print('YOU FELL TO YOUR DEATH')
        else:
            print('DEAD')

        self.gadget.stop()
        self.change_state(Player.STATE_DEAD)

    def render(self):
        flip_x = self.facing_x == -1
        self.order = 1

        if self.invisible:
            if self.state == Player.STATE_HIDDEN:
                self.sprite.play('HIDDEN', flip_x)
                self.order = -1
            else:
                if self.velocity_x != 0:
                    self.sprite.play('INVISIBLE_RUN', flip_x)
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

        elif self.state == Player.STATE_CLIMBING:
            if self.state_args['vertical']:
                if self.velocity_y != 0:
                    self.sprite.play('CLIMB_LADDER')
                    self.sprite.resume()
                else:
                    self.sprite.play('CLIMB_LADDER')
                    self.sprite.pause()
            else:
                graphics.set_color(125, 125, 125)
                graphics.draw_entity_rect(self)
                self.gadget.render()
                return

        elif self.state == Player.STATE_CROUCHING:
            if self.velocity_x != 0:
                self.sprite.play('CRAWL', flip_x)
            else:
                self.sprite.play('CROUCH', flip_x)

        elif self.state == Player.STATE_LEDGEGRAB:
            self.sprite.play('HANG', flip_x)

        elif self.state == Player.STATE_PUSHING:
            self.sprite.play('PUSH', flip_x)

        else:  # Default
            graphics.set_color(125, 125, 125)
            graphics.draw_entity_rect(self)
            self.gadget.render()
            return

        self.sprite.render(self.x, self.y)
        self.gadget.render()

    def update(self):
        temp_x = self.x
        temp_y = self.y
        has_solid_below = solid_below(self, self.x, self.y)

        # Key polling
        keydown_up = Key.down('up')
        keydown_down = Key.down('down')
        keydown_left = Key.down('left')
        keydown_right = Key.down('right')
        keydown_run = False  # Key.down('lshift')
        keypressed_up = Key.pressed('up')
        keypressed_down = Key.pressed('down')
        keypressed_left = Key.pressed('left')
        keypressed_right = Key.pressed('right')
        keypressed_jump = Key.pressed('space')
        keypressed_gadget = Key.pressed('x')

        if self.state == Player.STATE_STANDARD:
            # Run/Walk
            if keydown_left == keydown_right:
                self.velocity_x = 0
                self.walking_sound.stop()
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

                # Play walking sound effect
                if has_solid_below:
                    self.walking_sound.play(-1)
                else:
                    self.walking_sound.stop()

                # Push block
                block = peachy.collision.collides_group(
                    self.container, 'block',
                    self.at_point(temp_x + self.velocity_x, self.y)
                )
                if len(block) == 1 and has_solid_below:
                    block = block[0]
                    block_temp_x = block.x + self.velocity_x

                    if not peachy.collision.collides_solid(
                            self.container,
                            block.at_point(block_temp_x, block.y)):
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

                    if not collides_solid(self.container, test):
                        self.change_state(Player.STATE_LEDGEGRAB, ledge=ledge)
                        return

            # Interact
            if keydown_up:
                interactables = collides_group(self.container, 'interact', self)
                for interact in interactables:
                    if interact.member_of('rope'):
                        vertical = False
                        if interact.width == 0:
                            vertical = True
                        elif interact.height == 0:
                            vertical = False

                        self.change_state(Player.STATE_CLIMBING,
                                          handle=interact, vertical=vertical)

                        interact.attach(self)
                        return

                    elif interact.member_of('ladder'):
                        self.x = interact.x
                        self.change_state(Player.STATE_CLIMBING,
                                          handle=interact, vertical=True)
                        return

                    elif keypressed_up:
                        if interact.member_of('button'):
                            interact.press()

                        elif interact.member_of('door'):
                            if self.gadget.state == gadgets.Gadget.STATE_ACTIVE:
                                self.gadget.cancel()
                            interact.enter()

                        elif interact.member_of('lever'):
                            interact.pull()

                        elif interact.member_of('hiding-spot'):
                            self.change_state(Player.STATE_HIDDEN,
                                              hiding_spot=interact)
                            return

                        elif interact.member_of('message-box'):
                            interact.activate()
                            return

            # Climb down ladder
            if keypressed_down:
                ladder = collides_group(self.container, 'ladder',
                                        self.at_point(self.x, self.y + 1))
                if ladder:
                    ladder = ladder[0]
                    if self.y + self.height < ladder.y + ladder.height:
                        self.x = ladder.x
                        if self.y < ladder.y:
                            self.y = ladder.y
                        self.change_state(Player.STATE_CLIMBING,
                                          handle=ladder, vertical=True)
                        return

            # Pickup
            if keypressed_up:
                pickups = collides_group(self.container, 'pickup', self)
                for pickup in pickups:
                    if pickup.member_of('gadget'):
                        self.change_gadget(pickup.gadget)
                    elif pickup.member_of('key'):
                        self.obtained_keys.append(pickup.tag)
                        self.key_count += 1
                        pickup.destroy()

            # Crouching
            if keypressed_down and has_solid_below:
                self.change_state(Player.STATE_CROUCHING)
                return

            # Gravity
            if self.velocity_y < config.MAX_GRAVITY:
                self.velocity_y += config.GRAVITY

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
                            if handle.member_of('ladder'):
                                self.y = handle.y - self.height
                                self.change_state(Player.STATE_STANDARD)
                                return
                    if keydown_down:
                        if self.y + self.height < handle.y + handle.height:
                            self.velocity_y = Player.SPEED_SLOW
                        else:
                            self.velocity_y = 0
                            self.change_state(Player.STATE_STANDARD)
                            return
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

                        if not collides_solid(self.container, test):
                            self.x = test.x
                            self.facing_x *= -1
                            self.change_state(Player.STATE_LEDGEGRAB,
                                              ledge=ledge)
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
                temp_y = self.y - \
                    abs(Player.HEIGHT_STANDARD - Player.HEIGHT_CROUCH)
                if collides_solid(self.container,
                                  self.at_point(self.x, temp_y)):
                    self.height = Player.HEIGHT_CROUCH
                    temp_y = self.y
                    self.velocity_y = 0
                else:
                    self.state = Player.STATE_STANDARD
                    self.y = temp_y

            self.height = Player.HEIGHT_STANDARD
            if collides_solid(self.container, self.at_point(temp_x, temp_y)):
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

                    test = peachy.geo.Rect(
                        self.x, ledge.y - Player.HEIGHT_CROUCH,
                        self.width, Player.HEIGHT_CROUCH)
                    test.container = self.container

                    if test.x + test.width <= ledge.x:
                        test.x = ledge.x
                    elif test.x >= ledge.x + ledge.width:
                        test.x = ledge.x + ledge.width - test.width

                    if not collides_solid(self.container, test):
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
            if not rect_rect(self.at_point(test_x, self.y), block):
                self.change_state(Player.STATE_STANDARD)
                return

            block_temp_x = block.x + self.velocity_x
            if not collides_solid(self.container,
                                  block.at_point(block_temp_x, block.y)):
                block.x = block_temp_x

        # GADGET
        if self.state != Player.STATE_DEAD:
            if keypressed_gadget and self.gadget.name:
                self.gadget.use()

        # ADVANCE
        temp_x += self.velocity_x
        temp_y += self.velocity_y

        # LOCKED DOOR
        lock = collides_group(
            self.container, 'locked-door', self.at_point(temp_x, temp_y))
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
