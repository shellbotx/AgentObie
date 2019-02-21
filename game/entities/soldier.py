import math

import peachy
import peachy.geo
from peachy import graphics

from game.entities import Bullet
from game.utility import collision_resolution, get_line_segments, \
    raycast, solid_below, Graphic

from .player import Player

GRAVITY = 0.2
MAX_GRAVITY = 9


def angle_from_facing(fx, fy):
    """
    Get the degree angle from two facing indicators
    ex: Facing up right (-1, -1) is 30
    """

    if fx == 1 and fy == -1:
        return 30
    if fx == -1 and fy == -1:
        return 90
    if fx == -1 and fy == 0:
        return 150
    if fx == -1 and fy == 1:
        return 210
    if fx == 1 and fy == 1:
        return 270
    if fx == 1 and fy == 0:
        return 330


def facing_from_angle(angle):
    """
    Get a facing tuple from an angle.
    ex: 0 degrees means facing up (0, -1)
    """
    if angle > 360:
        angle %= 360

    if angle <= 30 or angle >= 330:
        return (1, 0)
    if angle <= 90:
        return (1, -1)
    if angle <= 150:
        return (-1, -1)
    if angle <= 210:
        return (-1, 0)
    if angle <= 270:
        return (-1, 1)
    if angle <= 330:
        return (1, 1)


class Soldier(peachy.Entity, peachy.geo.Rect):

    SIGHT_DISTANCE = 64
    AGGRO_DISTANCE = 56

    ATTACK_COOLDOWN = 90
    ALERT_TIMER = 60 * 2  # FPS * 5

    SPEED_ALERT = 1
    SPEED = 0.5
    SPEED_SLOW = 0.25

    STATE_IDLE = 'idle'
    STATE_ALERT = 'alert'
    STATE_PATROL = 'patrol'
    STATE_STUNNED = 'stun'

    STUN_DURATION = 60 * 3

    def __init__(self, x, y, stationary=False):
        super().__init__()
        super(peachy.geo.Rect).__init__(x, y, 8, 16)
        self.group = 'enemy liftable soldier can-slow can-stun'
        self.order = 2

        fx, fy = facing_from_angle(180)
        self.facing_x = fx
        self.facing_y = fy

        self.state = ''
        if stationary:
            self.state = Soldier.STATE_IDLE
        else:
            self.state = Soldier.STATE_PATROL

        self.attack_timer = Soldier.ATTACK_COOLDOWN / 2
        self.alert_timer = 0
        self.wait_timer = 0

        self.stunned = False
        self.stun_timer = 0
        self.slowed = False

        self.spotted_at = None

        ori = (4, 2)
        self.sprite = graphics.SpriteMap(
            peachy.fs.get_image('SoldierSpritesheet'), 18, 18)
        self.sprite.add('IDLE', [0], origin=ori)
        self.sprite.add('RUN', [5, 6, 7, 8, 9, 10, 11, 12], 4, True, origin=ori)

    def change_state(self, state, **kwargs):
        # previous_state = self.state
        self.state = state

        if state == Soldier.STATE_IDLE:
            self.facing_y = 0
            self.spotted_at = None
            self.attack_timer = Soldier.ATTACK_COOLDOWN / 2

        elif state == Soldier.STATE_PATROL:
            self.stunned = False
            self.facing_y = 0
            self.spotted_at = None
            self.attack_timer = Soldier.ATTACK_COOLDOWN / 2

        elif state == Soldier.STATE_ALERT:
            self.container.add(AlertAnimation(self))  # Play alert animation

            self.alert_timer = Soldier.ATTACK_COOLDOWN / 2
            self.velocity_x = 0
            self.spotted_at = kwargs['spotted']

        elif state == Soldier.STATE_STUNNED:
            self.velocity_x = 0
            self.stunned = True
            self.stun_timer = Soldier.STUN_DURATION

    def render(self):
        flip_x = self.facing_x == -1

        if self.state == Soldier.STATE_IDLE:
            self.sprite.play('IDLE', flip_x)
        elif (self.state == Soldier.STATE_ALERT or
              self.state == Soldier.STATE_PATROL):
            if self.velocity_x != 0:
                self.sprite.play('RUN', flip_x)
            else:
                self.sprite.play('IDLE', flip_x)
        else:
            graphics.set_color(255, 192, 203)

        self.render_light()

        graphics.set_color(255, 192, 203)
        self.sprite.render(self.x, self.y)

    def shoot(self, x, y, dx, dy):
        self.attack_timer = Soldier.ATTACK_COOLDOWN
        bullet = Bullet(x + self.width / 2, y + self.height / 2, dx, dy, 2)
        self.container.add(bullet)

    def update(self):
        temp_x = self.x
        temp_y = self.y
        player = self.container.get_name('player')
        distance_from_player = self.distance_from(player)
        pcx, pcy = player.center

        # All ladders that are below this entity are treated as solids in this
        # update. They are reverted back to this prior state at the end of the
        # update.
        altered_ladders = [l for l in self.container.get_group('ladder')
                           if l.y >= self.y + self.height]
        for l in altered_ladders:
            l._temp_soldier_solid = l.solid
            l.solid = True

        # Calculate player_visible
        player_visible = False
        view_obstructions = self.container.get_group('opaque')
        if distance_from_player <= 64 and not player.invisible and \
           player.state != Player.STATE_HIDDEN:
            if self.collides(player, self.x, self.y):
                player_visible = True
            else:
                opp = self.y - pcy
                adj = pcx - self.x
                angle = math.degrees(math.atan2(opp, adj))

                if angle < 0:
                    angle = 360 + angle

                sight_range = angle_from_facing(self.facing_x, self.facing_y)

                if sight_range <= angle <= sight_range + 60:
                    player_visible = \
                        raycast(self.x, self.y, pcx, pcy, view_obstructions)
                if sight_range + 60 >= 360:
                    angle = 360 - angle
                    if sight_range <= angle <= sight_range + 60:
                        player_visible = \
                            raycast(self.x, self.y, pcx, pcy, view_obstructions)

        if self.state == Soldier.STATE_IDLE:
            # TODO turn around, check behind you
            if player_visible:
                self.change_state(Soldier.STATE_ALERT, spotted=(pcx, pcy))

        elif self.state == Soldier.STATE_PATROL:
            if player_visible:
                self.change_state(Soldier.STATE_ALERT, spotted=(pcx, pcy))

            elif self.wait_timer > 0:
                self.wait_timer -= 1
                if self.wait_timer <= 0:
                    self.facing_x *= -1
            else:
                if solid_below(self, temp_x, temp_y):
                    tx = temp_x + self.width * self.facing_x
                    if self.collides_solid(tx, self.y) or \
                       not solid_below(self, tx, temp_y):
                        self.velocity_x = 0
                        self.wait_timer = 60
                    else:
                        if self.slowed:
                            self.velocity_x = Soldier.SPEED_SLOW * self.facing_x
                        else:
                            self.velocity_x = Soldier.SPEED * self.facing_x

        elif self.state == Soldier.STATE_ALERT:
            target_distance = 0
            if player_visible:
                self.alert_timer = Soldier.ALERT_TIMER
                target_distance = Soldier.AGGRO_DISTANCE
                self.spotted_at = (pcx, pcy)
            else:
                if self.alert_timer == Soldier.ALERT_TIMER:
                    # Player just went out of sight, therefore look where they
                    # would be. ie where they are this frame
                    self.spotted_at = (pcx, pcy)

                self.alert_timer -= 1
                if self.alert_timer <= 0:
                    self.change_state(Soldier.STATE_PATROL)
                    return
                target_distance = 12

            target = self.spotted_at

            # Compute facing angle
            opp = self.y - target[1]
            adj = target[0] - self.x
            player_angle = math.degrees(math.atan2(opp, adj))
            if player_angle < 0:
                player_angle = 360 + player_angle
            self.facing_x, self.facing_y = facing_from_angle(player_angle)

            dist_x_target = abs(self.center_x - target[0])
            # diff_y_target = self.center_y - target[1]

            # MOVEMENT
            if dist_x_target > target_distance:
                tx = temp_x + self.width * self.facing_x
                if solid_below(self, tx, temp_y) and not \
                   self.collides_solid(tx, self.y):
                    if self.slowed:
                        self.velocity_x = Soldier.SPEED_SLOW * self.facing_x
                    else:
                        self.velocity_x = Soldier.SPEED_ALERT * self.facing_x
                else:
                    self.wait_timer = 60
                    # self.facing_x *= -1
                    self.velocity_x = 0
            else:
                self.velocity_x = 0

            # ACTION
            if self.slowed:
                self.attack_timer -= 0.25
            else:
                self.attack_timer -= 1

            if self.attack_timer <= 0 and player_visible:
                self.shoot(self.x, self.y, self.facing_x, self.facing_y)

        elif self.state == Soldier.STATE_STUNNED:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stun_timer = 0
                self.state = Soldier.STATE_PATROL

        # GRAVITY
        if self.velocity_y < MAX_GRAVITY:
            self.velocity_y += GRAVITY

        # ADVANCE
        temp_x += self.velocity_x
        temp_y += self.velocity_y

        # FINALIZE
        c, self.x, self.y, self.velocity_x, self.velocity_y = \
            collision_resolution(self, temp_x, temp_y)

        # Undo solid ladders
        for l in altered_ladders:
            l.solid = l._temp_soldier_solid
            del l._temp_soldier_solid

    def GADGET_slow(self):
        self.slowed = True

    def GADGET_stun(self):
        self.change_state(Soldier.STATE_STUNNED)

    def GADGET_revert(self):
        self.slowed = False

    def render_light(self):
        # God, I wish I did a better job commenting this last year
        if self.state == Soldier.STATE_STUNNED:
            return

        angle = angle_from_facing(self.facing_x, self.facing_y)

        solids = self.container.get_group('opaque')

        # Disqualify any solids outside of range
        test_rect = Rect(self.x,
                         self.y - Soldier.SIGHT_DISTANCE * 0.75,
                         Soldier.SIGHT_DISTANCE, Soldier.SIGHT_DISTANCE * 1.25)
        if self.facing_x == -1:
            test_rect.x = self.x - Soldier.SIGHT_DISTANCE
        solids = [s for s in solids if s.collides(test_rect, s.x, s.y)]

        cx, cy = self.center
        points = []
        points.append((cx, cy))

        for degree in range(angle, angle + 61, 1):
            rad = math.radians(degree)
            dx = math.cos(rad)
            dy = math.sin(rad)
            length = Soldier.SIGHT_DISTANCE

            rpx = cx
            rpy = cy
            rdx = dx * length
            rdy = dy * length * -1

            # Find obstructions within the line of sight
            for solid in solids:
                # Get the raycast segments for this solid
                segments = None
                try:
                    segments = solid.segments
                    if solid.x != segments[0][0]:  # If the solid has moved
                        solid.refresh_segments()   # Refresh
                        segments = solid.segments
                except AttributeError:
                    segments = get_line_segments(solid)  # Get segments directly

                for segment in segments:
                    spx = segment[0]
                    spy = segment[1]
                    sdx = segment[2]
                    sdy = segment[3]

                    # Are the lines parallel? If so, there is no intersection
                    r_mag = math.sqrt(rdx * rdx + rdy * rdy)
                    s_mag = math.sqrt(sdx * sdx + sdy * sdy)
                    if (abs(rdx / r_mag) != abs(sdx / s_mag)) or \
                       (abs(rdy / r_mag) != abs(sdy / s_mag)):

                        T2 = (rdx * (spy - rpy) + rdy * (rpx - spx)) /\
                             (sdx * rdy - sdy * rdx)
                        T1 = (spx + sdx * T2 - rpx) / rdx

                        if T1 >= 0 and T2 >= 0 and T2 <= 1:
                            if T1 * Soldier.SIGHT_DISTANCE < length:
                                length = T1 * Soldier.SIGHT_DISTANCE

            # Append collisions along line to simulate blocked line of sight
            points.append((rpx + dx * length, rpy - dy * length))

        if self.state == Soldier.STATE_ALERT:
            graphics.set_color(255, 0, 0, 64)
        else:
            graphics.set_color(255, 165, 0, 32)
        graphics.draw_polygon(points)


class AlertAnimation(Graphic):

    def __init__(self, soldier):
        soldier_spritesheet = peachy.fs.get_image('SoldierSpritesheet')
        alert_icon = graphics.splice(soldier_spritesheet, 18, 18)[3]
        super().__init__(soldier.x, soldier.y, alert_icon, 20)
        self.soldier = soldier

    def update(self):
        off_y = self.image.get_height()

        self.x = self.soldier.x - 4
        self.y = self.soldier.y - off_y
        super(AlertAnimation, self).update()
