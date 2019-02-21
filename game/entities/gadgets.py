import copy
import peachy
import peachy.geo
import random
from game.config import GRAVITY, MAX_GRAVITY
from game.utility import Particle


def from_name(name, player):
    if name == 'NONE':
        return Gadget(player, '')
    elif name == 'DUPLICATE':
        return BodyDuplicator(player)
    elif name == 'FLASH':
        return FlashBangLauncher(player)
    elif name == 'INVISIBLE' or name == 'INVS':
        return InvisibilityCloak(player)
    elif name == 'STUN':
        return StunBomb(player)
    elif name == 'TIME':
        return TimeDisruptor(player)
    else:
        print('[WARN] Gadget "{0}" does not exist'.format(name))
        return Gadget(player, '')


class Gadget(object):

    STATE_ACTIVE = 0
    STATE_INACTIVE = 1
    STATE_COOLDOWN = 2

    def __init__(self, player, name):
        self.player = player
        self.name = name
        self.timer = 0  # TODO Change to peachy.utils.Counter
        self.state = Gadget.STATE_INACTIVE

    def cancel(self):
        return

    def use(self):
        return

    def draw_particles(self, accent=(255, 0, 255)):
        x = self.player.x
        y = self.player.y
        w = self.player.width
        h = self.player.height

        grey = (125, 125, 125)
        black = (0, 0, 0)

        for i in range(12):
            if i % 2 == 0:
                color = random.choice([accent, grey, black])
            else:
                color = accent

            px = random.randint(int(x - w), int(x + w * 2))
            py = random.randint(int(y - h), int(y + h * 2))
            lifespan = random.randint(10, 30)
            speed = random.randint(1, 20) * 0.1
            radius = random.randint(2, 4)

            p = self.player.container.add(
                Particle(px, py, speed, 0, radius, lifespan, color))
            if i < 4:
                p.order = -1
            else:
                p.order = 2

    def render(self):
        return

    def stop(self):
        self.timer = 0
        self.state = Gadget.STATE_INACTIVE

    def update(self):
        return


class BodyDuplicator(Gadget):

    NAME = 'DUPLICATE'
    COOLDOWN = 5 * 60
    DURATION = 5 * 60

    def __init__(self, player):
        super().__init__(player, BodyDuplicator.NAME)
        self.duplicate = None

    def stop(self):
        super().stop()
        if self.duplicate:
            self.duplicate.destroy()
            self.duplicate = None

    def update(self):
        if self.timer > 0:
            self.timer -= 1

        if self.timer <= 0:
            if self.state == Gadget.STATE_ACTIVE:
                self.state = Gadget.STATE_COOLDOWN
                self.stop()
                self.timer = BodyDuplicator.COOLDOWN

            elif self.state == Gadget.STATE_COOLDOWN:
                self.state = Gadget.STATE_INACTIVE

    def use(self):
        if self.duplicate is not None:
            self.duplicate.destroy()
            self.duplicate = None

        self.state = Gadget.STATE_ACTIVE
        self.timer = BodyDuplicator.DURATION
        self.duplicate = BodyDuplication(self.player)
        self.player.container.add(self.duplicate)
        self.draw_particles((0, 255, 0))


class BodyDuplication(peachy.Entity):

    def __init__(self, player):
        super().__init__(player.x, player.y)
        self.group = 'player duplicate'

        self.width = player.width
        self.height = player.height

        self.state = player.state
        self.state_args = player.state_args

        self.sprite = copy.copy(player.sprite)
        self.sprite.pause()

        self.timer = peachy.utils.Counter(0, BodyDuplicator.DURATION)
        self.order = 0

    def render(self):
        peachy.graphics.set_color(0, 255, 0)
        peachy.graphics.draw_entity_rect(self)
        self.sprite.render(self.x, self.y)

    def update(self):
        if self.timer.tick():
            self.destroy()


class FlashBangLauncher(Gadget):

    NAME = 'FLASH'
    COOLDOWN = 60 * 5

    def __init__(self, player):
        super().__init__(player, FlashBangLauncher.NAME)

    def use(self):
        if self.state == Gadget.STATE_INACTIVE:
            self.state = Gadget.STATE_ACTIVE

            grenade = FlashBangGrenade(self.player.x, self.player.y, self.player.facing_x)
            self.player.container.add(grenade)

            self.timer = FlashBangLauncher.COOLDOWN

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        elif self.state == Gadget.STATE_ACTIVE:
            self.state = Gadget.STATE_INACTIVE


class FlashBangGrenade(peachy.Entity):

    STATE_DORMANT = 0
    STATE_EXPLODE = 1

    def __init__(self, x, y, dx):
        super().__init__(x, y)
        self.width = 3
        self.height = 3
        self.duration = peachy.utils.Counter(0, 60 * 3)

        self.velocity_x = dx * 2
        self.velocity_y = -3.5

        self.state = FlashBangGrenade.STATE_DORMANT

    def render(self):
        if self.state == FlashBangGrenade.STATE_DORMANT:
            peachy.graphics.set_color(242, 133, 0)
            peachy.graphics.draw_circle(self.x - 1.5, self.y - 1.5, 3)
        elif self.state == FlashBangGrenade.STATE_EXPLODE:
            peachy.graphics.set_color(255, 255, 255)
            peachy.graphics.draw_circle(self.x - 32, self.y - 32, 32)

    def pop(self):
        self.state = FlashBangGrenade.STATE_EXPLODE
        self.duration.target = 30
        self.duration.reset()

        # Do collision test
        ents = self.container.get_group('can-slow')
        for entity in ents:
            if entity.collides_circle((self.x, self.y, 32)):
                if not entity.slowed:
                    entity.GADGET_slow()

    def update(self):
        if self.state == FlashBangGrenade.STATE_DORMANT:
            temp_x = self.x
            temp_y = self.y

            if not self.duration.tick():
                self.pop()
                return

            if self.velocity_y < MAX_GRAVITY:
                self.velocity_y += (GRAVITY * 0.75)

            temp_x += self.velocity_x
            temp_y += self.velocity_y

            collisions = self.collides_solid(temp_x, temp_y)
            for collision in collisions:
                if not self.collides(collision, temp_x, temp_y):
                    continue
                elif self.collides(collision, temp_x, self.y):
                    temp_x = self.x
                    self.velocity_x *= -0.5
                elif self.collides(collision, self.x, temp_y):
                    temp_y = self.y
                    self.velocity_x *= 0.5
                    self.velocity_y *= -0.6
                else:
                    temp_x = self.x
                    temp_y = self.y

            self.x = temp_x
            self.y = temp_y

        elif self.state == FlashBangGrenade.STATE_EXPLODE:
            if not self.duration.tick():
                self.destroy()


class StunBomb(Gadget):

    NAME = 'STUN'
    COOLDOWN = 60 * 2
    DURATION = 60 * 0.25
    MAX_RADIUS = 32

    def __init__(self, player):
        super().__init__(player, StunBomb.NAME)
        self.radius = 0

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
            peachy.graphics.draw_circle(self.x - self.radius,
                                        self.y - self.radius, self.radius)

    def update(self):
        if self.timer > 0:
            self.timer -= 1

        if self.state == Gadget.STATE_ACTIVE:
            self.radius = StunBomb.MAX_RADIUS * \
                float(float(StunBomb.DURATION - self.timer) / StunBomb.DURATION)
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
        super().__init__(player, InvisibilityCloak.NAME)

    def cancel(self):
        if self.state == Gadget.STATE_ACTIVE:
            self.state = Gadget.STATE_COOLDOWN
            self.timer = InvisibilityCloak.COOLDOWN
            self.player.invisible = False

    def stop(self):
        super().stop()
        self.player.invisible = False

    def update(self):
        if self.timer > 0:
            self.timer -= 1

        if self.state == Gadget.STATE_ACTIVE:
            if self.timer <= 0:
                self.cancel()

        elif self.state == Gadget.STATE_COOLDOWN:
            if self.timer <= 0:
                self.state = Gadget.STATE_INACTIVE
                self.timer = 0

    def use(self):
        if self.state == Gadget.STATE_INACTIVE:
            self.state = Gadget.STATE_ACTIVE
            self.timer = InvisibilityCloak.DURATION
            self.player.invisible = True
            self.draw_particles((0, 171, 192))


class TimeDisruptor(Gadget):

    NAME = 'TIME'
    COOLDOWN = 60 * 2
    DURATION = 60 * 3
    RADIUS = 32

    def __init__(self, player):
        super().__init__(player, TimeDisruptor.NAME)

    def use(self):
        if self.state == Gadget.STATE_INACTIVE:
            self.state = Gadget.STATE_ACTIVE
            self.timer = TimeDisruptor.DURATION
            self.x = self.player.x + self.player.width / 2 - TimeDisruptor.RADIUS
            self.y = self.player.y + self.player.height / 2 - TimeDisruptor.RADIUS
            self.draw_particles((183, 71, 133))

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
