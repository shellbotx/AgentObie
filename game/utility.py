import peachy
    
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

            '''
            elif collision.member_of('solid') and collision.slanted:
                
                # TODO fix snag at top of slope

                left = collision.intersection(x)
                right = collision.intersection(x + entity.width)

                if y + entity.height > left or y + entity.height > right:
                    if collision.y < left < right:
                        y = left - entity.height
                    elif collision.y < right < left:
                        y = right - entity.height
                    else:
                        y = collision.y - entity.height
                    vel_y = 0
            '''

        elif not entity.collides(collision, entity.x, y):
            if x - entity.width - vel_x < collision.x and vel_x > 0:
                x = collision.x - entity.width
            elif x + vel_x > collision.x - collision.width and vel_x < 0:
                x = collision.x + collision.width
            vel_x = 0
            
        elif not entity.collides(collision, x, entity.y):
            if y - entity.height - vel_y < collision.y and vel_y > 0:
                y = collision.y - entity.height
            elif y + vel_y > collision.y - collision.height and vel_y < 0:
                y = collision.y + collision.height
            vel_y = 0

        else:
            x = entity.x
            y = entity.y
            vel_x = 0
            vel_y = 0
            break

    collision_occurred = len(collisions) > 0
    return collision_occurred, x, y, vel_x, vel_y

def solid_below(entity, x, y):
    return entity.collides_solid(x, y + 1)

def solid_left(entity, x, y):
    return entity.collides_solid(x - 1, y)

def solid_right(entity, x, y):
    return entity.collides_solid(x + 1, y)
