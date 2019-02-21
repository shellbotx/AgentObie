import peachy
from peachy.collision import collides_solid, line_line
import math


def collision_resolution(entity, x, y):

    # basic platformer collision resolution routine
    # TODO fix spacing. for some reason certain collisions allow for a gap in
    # space (between 1 and 2 pixels wide)

    vel_x = entity.velocity_x
    vel_y = entity.velocity_y

    collision_results = collides_solid(entity.container, entity.at_point(x, y))
    for result in collision_results:
        colliding = result.function
        other = result.shape

        # Check if collision is resolved, on y axis, or on x axis
        test_a = (other, entity.at_point(x, y))
        test_b = (other, entity.at_point(x, entity.y))
        test_c = (other, entity.at_point(entity.x, y))

        if not result.is_first:
            test_a = test_a[1], test_a[0]
            test_b = test_b[1], test_b[0]
            test_c = test_c[1], test_c[0]

        # collision already resolved
        if not colliding(*test_a):
            continue

        # collision resolved by reverting y axis
        elif not colliding(*test_b):
            if y - entity.height - vel_y < other.y and vel_y > 0:
                y = other.y - entity.height
            elif y + vel_y > other.y - other.height and vel_y < 0:
                y = other.y + other.height
            vel_y = 0

        # collision resolved by reverting x axis
        elif not colliding(*test_c):
            if x - entity.width - vel_x < other.x and vel_x > 0:
                x = other.x - entity.width
            elif x + vel_x > other.x - other.width and vel_x < 0:
                x = other.x + other.width
            vel_x = 0

        # collision resoultion not found, revert to original space
        else:
            x = entity.x
            y = entity.y
            vel_x = 0
            vel_y = 0
            break

    collision_occurred = len(collision_results) > 0
    return collision_occurred, x, y, vel_x, vel_y


def dxdy_from_string(direction):
    dx = 0
    dy = 0

    if direction == 'LEFT':
        dx = -1
    elif direction == 'RIGHT':
        dx = 1
    elif direction == 'UP':
        dy = -1
    elif direction == 'DOWN':
        dy = 1

    return dx, dy


def draw_message(player, message):
    HEIGHT = 64
    y = 0

    if player.y + player.height < HEIGHT:
        y = peachy.PC().canvas_height - HEIGHT

    peachy.graphics.set_color(0, 30, 60)
    peachy.graphics.draw_rect(0, y, peachy.PC().canvas_width, HEIGHT)
    peachy.graphics.set_color(255, 255, 255)
    peachy.graphics.draw_text(message, 8, y + 8)


def get_line_segments(e):
    return [[e.x, e.y, e.width, 0],  # Top
            [e.x + e.width, e.y, 0, e.height],   # Right
            [e.x + e.width, e.y + e.height, -e.width, 0],   # Bottom
            [e.x, e.y + e.height, 0, -e.height]]   # Left


def raycast(sx, sy, ex, ey, obstructions):
    lineA1 = (sx, sy)
    lineA2 = (ex, ey)

    for obstruction in obstructions:
        segments = []
        try:
            segments = obstruction.segments
        except(AttributeError, IndexError):
            segments = get_line_segments(obstruction)

        for segment in segments:
            lineB1 = (segment[0], segment[1])
            lineB2 = (segment[0] + segment[2], segment[1] + segment[3])
            if line_line(lineA1, lineA2, lineB1, lineB2):
                return False
    return True


def solid_below(entity, x, y):
    return collides_solid(entity.container, entity.at_point(x, y + 1))


def solid_left(entity, x, y):
    return collides_solid(entity.container, entity.at_point(x - 1, y))


def solid_right(entity, x, y):
    return collides_solid(entity.container, entity.at_point(x + 1, y))


def string_escape(string):
    # Convert raw string to unicode string
    return bytes(string, 'utf-8').decode('unicode-escape')


class CheckpointData(object):
    def __init__(self):
        self.stage = ''
        self.gadget = ''
        self.keys = []  # TODO
        self.open_doors = []  # TODO

    @staticmethod
    def generate(stage):
        checkpoint = CheckpointData()
        checkpoint.stage = stage.stage_data.path
        checkpoint.gadget = stage.player.gadget.name
        checkpoint.open_doors = []
        return checkpoint


class Graphic(peachy.Entity):
    """ Display an image for a duration, then delete it """
    def __init__(self, x, y, image, duration):
        peachy.Entity.__init__(self, x, y)
        self.image = image
        self.duration = duration

    def render(self):
        peachy.graphics.draw(self.image, self.x, self.y)

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.destroy()


class ParallaxBG(object):

    def __init__(self, max_width, max_height):
        self.width = max_width
        self.height = max_height

        self.x = None
        self.y = None

        self.layers = []

        self.paused = False

    def create_layer(self, image, velocity, tile_x, tile_y):
        layer = ParallaxBG._Layer(self, image, velocity, tile_x, tile_y)
        self.layers.append(layer)
        return layer

    def pause(self):
        self.paused = True

    def render(self, x, y):
        for layer in self.layers:
            if not self.paused:
                layer.move()
            layer.render(x, y)

    def resume(self):
        self.paused = False

    class _Layer(object):
        def __init__(self, parent, image, velocity, tile_x, tile_y):
            self.image = image
            self.width, self.height = self.image.get_size()
            self.velocity = velocity

            self.x = 0
            self.y = 0

            self.tile_x = tile_x
            self.tile_y = tile_y

            self.max_x = parent.width
            self.max_y = parent.height

        def move(self):
            self.x = (self.x + self.velocity.x) % self.width
            self.y = (self.y + self.velocity.y) % self.height

        def render(self, view_x, view_y, invert=False):
            if self.tile_x and self.tile_y:
                off_x = view_x - self.width
                while off_x < self.max_x + view_x + self.width:
                    off_y = view_y - self.height
                    while off_y < self.max_y + view_y + self.height:
                        peachy.graphics.draw(self.image, self.x + off_x,
                                             self.y + off_y)
                        off_y += self.height
                    off_x += self.width

            elif self.tile_x:
                off_x = view_x - self.width
                while off_x < self.max_x + view_x + self.width:
                    peachy.graphics.draw(self.image, self.x + off_x, view_y)
                    off_x += self.width

            elif self.tile_y:
                off_y = view_y - self.height
                while off_y < self.max_y + view_y + self.height:
                    peachy.graphics.draw(self.image, view_x, self.y + off_y)
                    off_y += self.width

            else:
                x = self.x + view_x
                y = self.y + view_y
                peachy.graphics.draw(self.image, x, y)


class Particle(peachy.Entity):
    """ TODO Remove from container.entities and add to container.particles
    to speed up get_group and get_name """

    def __init__(self, x, y, speed=1, angle=0, radius=0, lifespan=1,
                 color=(0, 0, 0)):
        super().__init__(x, y)
        self.speed = speed
        self.angle = angle
        self.radius = radius
        self.duration = peachy.utils.Counter(0, lifespan)
        self.color = color

    def render(self):
        peachy.graphics.set_color(*self.color)
        peachy.graphics.draw_circle(self.x, self.y, self.radius)

    def update(self):
        if self.duration.tick():
            self.destroy()
        else:
            self.x += math.sin(self.angle) * self.speed
            self.y -= math.cos(self.angle) * self.speed
