import peachy

class Image(peachy.Entity):
    ''' Display an image for a duration, then deletes it '''
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
    
class Rect(peachy.Entity):
    def __init__(self, x, y, width=None, height=None):
        if width is None or height is None:
            width = x
            height = y
            x = 0
            y = 0
        peachy.Entity.__init__(self, x, y)
        self.width = width
        self.height = height

def collision_resolution(entity, x, y):

    # basic platformer collision resolution routine
    # TODO fix spacing. for some reason certain collisions allow for a gap in space etc

    vel_x = entity.velocity_x
    vel_y = entity.velocity_y

    collisions = entity.collides_solid(x, y)
    for collision in collisions:

        if not entity.collides(collision, x, y):
            continue

        elif not entity.collides(collision, x, entity.y):
            if y - entity.height - vel_y < collision.y and vel_y > 0:
                y = collision.y - entity.height
            elif y + vel_y > collision.y - collision.height and vel_y < 0:
                y = collision.y + collision.height
            vel_y = 0

        elif not entity.collides(collision, entity.x, y):
            if x - entity.width - vel_x < collision.x and vel_x > 0:
                x = collision.x - entity.width
            elif x + vel_x > collision.x - collision.width and vel_x < 0:
                x = collision.x + collision.width
            vel_x = 0

        else:
            x = entity.x
            y = entity.y
            vel_x = 0
            vel_y = 0
            break

    collision_occurred = len(collisions) > 0
    return collision_occurred, x, y, vel_x, vel_y

def draw_message(player, message):
    HEIGHT = 64
    y = 0

    if player.y + player.height < HEIGHT:
        y = peachy.PC.height - HEIGHT
    
    peachy.graphics.set_color(0, 30, 60)
    peachy.graphics.draw_rect(0, y, peachy.PC.width, HEIGHT)
    peachy.graphics.set_color(255, 255, 255)
    peachy.graphics.draw_text(message, 8, y + 8)

def get_line_segments(entity):
    return [ [entity.x, entity.y, entity.width, 0], 
             [entity.x + entity.width, entity.y, 0, entity.height], 
             [entity.x + entity.width, entity.y + entity.height, -entity.width, 0], 
             [entity.x, entity.y + entity.height, 0, -entity.height]]

def line_line_collision(lineA1, lineA2, lineB1, lineB2):
    denominator = ((lineB2[1] - lineB1[1]) * (lineA2[0] - lineA1[0])) - \
                  ((lineB2[0] - lineB1[0]) * (lineA2[1] - lineA1[1]))

    if denominator == 0:
        return False
    else:
        ua = (((lineB2[0] - lineB1[0]) * (lineA1[1] - lineB1[1])) - \
              ((lineB2[1] - lineB1[1]) * (lineA1[0] - lineB1[0]))) / denominator

        ub = (((lineA2[0] - lineA1[0]) * (lineA1[1] - lineB1[1])) - \
              ((lineA2[1] - lineA1[1]) * (lineA1[0] - lineB1[0]))) / denominator

        if (ua < 0) or (ua > 1) or (ub < 0) or (ub > 1):
            return False
        return True

def raycast(sx, sy, ex, ey, obstructions):
    lineA1 = (sx, sy)
    lineA2 = (ex, ey)

    for obstruction in obstructions:
        segments = []
        try:
            segments = obstruction.segments
        except AttributeError, IndexError:
            segments = get_line_segments(obstruction)

        for segment in segments:
            lineB1 = (segment[0], segment[1])
            lineB2 = (segment[0] + segment[2], segment[1] + segment[3])
            if line_line_collision(lineA1, lineA2, lineB1, lineB2):
                return False
    return True

def solid_below(entity, x, y):
    return entity.collides_solid(x, y + 1)

def solid_left(entity, x, y):
    return entity.collides_solid(x - 1, y)

def solid_right(entity, x, y):
    return entity.collides_solid(x + 1, y)
