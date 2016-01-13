import peachy
from game.utility import collision_resolution, solid_below, Rect

from player import Player

GRAVITY = 0.2
MAX_GRAVITY = 9

class Soldier(peachy.Entity):

    AGGRO_DISTANCE = 96

    ATTACK_COOLDOWN = 30
    
    SPEED_ALERT = 1
    SPEED = 0.5
    SPEED_SLOW = 0.15

    STATE_IDLE = 'idle'
    STATE_ALERT = 'alert'
    STATE_PATROL = 'patrol'
    STATE_STUNNED = 'stun'

    STUN_DURATION = 60 * 3

    def __init__(self, x, y, stationary=False):
        peachy.Entity.__init__(self, x, y)
        self.group = 'enemy liftable soldier can-slow can-stun'
        self.width = 8
        self.height = 12
        
        if stationary:
            self.state = Soldier.STATE_IDLE
        else:
            self.state = Soldier.STATE_PATROL

        self.facing_x = 1
        self.attack_timer = 0

        self.stunned = False
        self.stun_timer = 0
        self.slowed = False

    def render(self):
        if self.state == Soldier.STATE_ALERT:
            peachy.graphics.set_color(255, 0, 0)
        elif self.state == Soldier.STATE_STUNNED:
            peachy.graphics.set_color(255, 255, 51)
        elif self.slowed:
            peachy.graphics.set_color(0, 0, 255)
        else:
            peachy.graphics.set_color(255, 192, 203)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def change_state(self, state):
        if state == Soldier.STATE_IDLE:
            x = 0
        elif state == Soldier.STATE_PATROL:
            self.stunned = False
        elif state == Soldier.STATE_ALERT:
            self.velocity_x = 0
        elif state == Soldier.STATE_STUNNED:
            self.velocity_x = 0
            self.stunned = True
            self.stun_timer = Soldier.STUN_DURATION

        self.state = state

    def check_LOS(self, player):  # LOS = Line of Sight

        if player.state == Player.STATE_HIDING:
            return False

        test_x = 0
        test_width = abs(self.x - player.x)

        if self.facing_x == -1 and player.x < self.x:
            test_x = player.x
        elif self.facing_x == 1 and player.x > self.x:
            test_x = self.x
        else:
            return False

        diff_y = player.y - self.y
        if diff_y <= self.height and diff_y > player.height * -1:
            LOS = Rect(test_x, self.y, test_width, self.height)
            LOS.container = self.container

            if not LOS.collides_solid() and not LOS.collides_group('solid'):
                return True
        else:
            return False

    def update(self):
        temp_x = self.x
        temp_y = self.y

        player = self.container.get_name('player')
        player_visible = self.check_LOS(player)
        distance_from_player = abs(player.x - self.x)
        
        if player.invisible:
            player_visible = False
        
        if self.state == Soldier.STATE_IDLE:
            if player_visible:
                self.change_state(Soldier.STATE_ALERT)

        elif self.state == Soldier.STATE_PATROL:
            if player_visible:
                self.change_state(Soldier.STATE_ALERT)
                return

            if solid_below(self, temp_x + self.width * self.facing_x, temp_y):
                if self.slowed:
                    self.velocity_x = Soldier.SPEED_SLOW * self.facing_x
                else:
                    self.velocity_x = Soldier.SPEED * self.facing_x
            else:
                self.velocity_x = 0
                self.facing_x *= -1

        elif self.state == Soldier.STATE_ALERT:
            if player_visible:
                if self.slowed:
                    self.attack_timer -= 0.25
                else:
                    self.attack_timer -= 1
                if self.attack_timer <= 0:
                    self.attack_timer = Soldier.ATTACK_COOLDOWN
                    bullet = SoldierBullet(self.x, self.y + 6, self.facing_x)
                    self.container.add(bullet)

            if distance_from_player > Soldier.AGGRO_DISTANCE:
                if solid_below(self, temp_x + self.width * self.facing_x, temp_y):
                    if self.slowed:
                        self.velocity_x = Soldier.SPEED_SLOW * self.facing_x
                    else:
                        self.velocity_x = Soldier.SPEED_ALERT * self.facing_x
                else:
                    self.velocity_x = 0
                    self.facing_x *= -1

        elif self.state == Soldier.STATE_STUNNED:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stun_timer = 0
                self.state = Soldier.STATE_PATROL

        temp_x += self.velocity_x
        temp_y += self.velocity_y

        c, self.x, self.y, self.velocity_x, self.velocity_y = \
            collision_resolution(self, temp_x, temp_y)

        if c:
            self.facing_x *= -1

    def GADGET_slow(self):
        self.slowed = True

    def GADGET_stun(self):
        self.change_state(Soldier.STATE_STUNNED)

    def GADGET_revert(self):
        self.slowed = False


class SoldierBullet(peachy.Entity):

    SPEED = 2
    SPEED_SLOW = 0.5

    def __init__(self, x, y, direction_x):
        peachy.Entity.__init__(self, x, y)
        self.group = 'can-slow'

        self.width = 4
        self.height = 4
        self.direction_x = direction_x

        self.slowed = False

    def render(self):
        if self.slowed:
            peachy.graphics.set_color(0, 0, 255)
        else:
            peachy.graphics.set_color(255, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        player = self.container.get_name('player')

        if self.slowed:
            self.x += SoldierBullet.SPEED_SLOW * self.direction_x
        else:
            self.x += SoldierBullet.SPEED * self.direction_x

        if self.collides_solid() or self.collides_group('solid'):
            self.destroy()
        if self.collides(player, self.x, self.y):
            player.kill(self)
            self.destroy()

    def GADGET_slow(self):
        self.slowed = True

    def GADGET_revert(self):
        self.slowed = False