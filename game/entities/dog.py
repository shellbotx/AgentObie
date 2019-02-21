import peachy
import peachy.geo

from game.config import GRAVITY, MAX_GRAVITY
from game.utility import collision_resolution, solid_below


class Dog(peachy.Entity, peachy.geo.Rect):

    AGGRO_COOLDOWN = 3 * 60
    AGGRO_RADIUS = 36

    STATE_STANDARD = 'standard'
    STATE_AGGRO = 'aggro'
    STATE_STUNNED = 'distracted'

    SPEED_WALK = 0.5
    SPEED_RUN = 1.5

    def __init__(self, x, y):
        super(peachy.Entity).__init__()
        super(peachy.geo.Rect).__init__(x, y, 16, 10)
        self.group = 'enemy liftable dog can-slow can-stun'
        self.order = 2

        self.facing_x = -1
        self.facing_y = 0

        self.state = Dog.STATE_STANDARD

        self.aggro_timer = peachy.utils.Counter(0, Dog.AGGRO_COOLDOWN)
        self.stun_timer = 300

        self.sprite = peachy.fs.get_image('assets/img/dog.png')

    def bite(self, player):
        if player.member_of('duplicate'):
            player.destroy()
            self.state = Dog.STATE_STUNNED
            self.velocity_x = 0
        else:
            player.kill(self)

    def change_state(self, state, **kwargs):
        self.state = state

    def render(self):
        peachy.graphics.set_color(254, 154, 4)
        peachy.graphics.draw_entity_rect(self)

        x, y = self.center
        if self.state == Dog.STATE_AGGRO:
            peachy.graphics.set_color(255, 0, 0, 25)
        elif self.state == Dog.STATE_STUNNED:
            peachy.graphics.set_color(255, 0, 255, 25)
        else:
            peachy.graphics.set_color(255, 255, 255, 25)
        peachy.graphics.draw_circle(x - Dog.AGGRO_RADIUS, y - Dog.AGGRO_RADIUS,
                                    Dog.AGGRO_RADIUS)

        if self.facing_x == -1:
            peachy.graphics.draw(self.sprite, self.x, self.y - 3,
                                 args=peachy.graphics.FLIP_X)
        else:
            peachy.graphics.draw(self.sprite, self.x, self.y - 3)

    def update(self):
        temp_x = self.x
        temp_y = self.y
        cx, cy = self.center

        players = self.container.get_group('player')

        target = None
        target_distance = None
        target_visible = False
        tcx, tcy = (0, 0)

        # Aggro closest player
        for player in players:
            temp_distance = self.distance_from(player)
            if target_distance is None or temp_distance < target_distance:
                target = player
                target_distance = temp_distance
                tcx, tcy = target.center

        # Visibility
        target_distance
        if target_distance <= Dog.AGGRO_RADIUS:
            if target_distance <= Dog.AGGRO_RADIUS:
                target_visible = True
            # Bite
            if self.collides(target, self.x, self.y) and \
               self.state != Dog.STATE_STUNNED:
                self.bite(target)

        # Update state
        if self.state == Dog.STATE_STANDARD:
            # Movement
            if solid_below(self, temp_x + self.width * self.facing_x, temp_y) and not \
               self.collides_solid(temp_x + self.width * self.facing_x, self.y):
                self.velocity_x = Dog.SPEED_WALK * self.facing_x
            else:
                self.velocity_x = 0
                self.facing_x *= -1

            # Detect player
            if target_visible:
                self.change_state(Dog.STATE_AGGRO)

        elif self.state == Dog.STATE_AGGRO:
            if target_distance > Dog.AGGRO_RADIUS:
                if not self.aggro_timer.tick():
                    self.change_state(Dog.STATE_STANDARD)
                self.velocity_x = 0
            else:
                self.aggro_timer.reset()

                x_dist = abs(cx - tcx)
                if x_dist > (self.width / 2):
                    x_dist = cx - tcx
                    if x_dist < 0:
                        self.facing_x = 1
                    else:
                        self.facing_x = -1

                    if solid_below(self, temp_x + self.width * self.facing_x, temp_y):
                        self.velocity_x = Dog.SPEED_RUN * self.facing_x
                    else:
                        self.velocity_x = 0
                else:
                    self.velocity_x = 0

        elif self.state == Dog.STATE_STUNNED:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = Dog.STATE_STANDARD

        # Finalize
        if self.velocity_y < MAX_GRAVITY:
            self.velocity_y += GRAVITY

        temp_x += self.velocity_x
        temp_y += self.velocity_y

        c, self.x, self.y, self.velocity_x, self.velocity_y = \
            collision_resolution(self, temp_x, temp_y)
