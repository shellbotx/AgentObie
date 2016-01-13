import collections

import peachy 
from peachy import PC

PLACE_ACTOR = 'place_actor'
WAIT = 'wait'

class Scene(object):

    def __init__(self):
        self.actors = {}
        self.directions = collections.deque()
        self.create()

        self.current_direction = None
        self.direction_timer = 0

    def render(self):
        for _, actor in self.actors.iteritems():
            if not actor.hidden:
                actor.render()

    def update(self):

        end_turn = False

        while not end_turn and len(self.directions) > 0:

            direction = self.directions[0]

            if direction[0] == PLACE_ACTOR:
                actor = self.actors[direction[1]]
                actor.x = int(direction[2])
                actor.y = int(direction[3])

                if actor.hidden:
                    actor.hidden = False
                
                self.directions.popleft()

            elif direction[0] == WAIT:
                self.direction_timer += 1

                print self.direction_timer

                if self.direction_timer <= int(direction[1]):
                    end_turn = True
                else:
                    self.direction_timer = 0
                    self.directions.popleft()

            if not self.directions:
                # TODO exit scene
                print 'wait'
                self.add_direction(WAIT, 10)
                end_turn = True

    
    def add_actor(self, name, actor):
        self.actors[name] = actor

    def add_direction(self, *args):
        try:
            direction = args[0]
            
            if direction == PLACE_ACTOR:
                actor = args[1]
                x = args[2]
                y = args[3]

            elif direction == WAIT:
                wait_time = args[1]

            elif direction == 'start_level':
                level_name = args[1]

        except IndexError:
            print '[ERROR] Invalid stage direction: {0}'.format(args)
            raise

        self.directions.append(args)


class TestScene(Scene):

    def __init__(self):
        Scene.__init__(self)

    def create(self):
        # Actors
        self.add_actor('obie', Obie())
        
        # Directions
        self.add_direction(PLACE_ACTOR, 'obie', 100, 100)
        self.add_direction(WAIT, PC.fps * 3)

        self.add_direction(PLACE_ACTOR, 'obie', 200, 200)
        self.add_direction(WAIT, PC.fps * 3)

        # self.direction(DISPLAY_MESSAGE, 'This is a test message')
        # self.add_direction(START_LEVEL, 'TEST')

        
class Actor(object):
    def __init__(self, image_path=''):
        if image_path:
            self.image = peachy.assets.get_image(image_path)
        else:
            self.image = None

        self.x = 0
        self.y = 0
        self.hidden = True

    def render(self):
        peachy.graphics.draw_image(self.image, self.x, self.y)

    def update(self):
        return


class Obie(Actor):
    def __init__(self):
        Actor.__init__(self)#, 'assets/obie.png')

        # sprites = peachy.graphics.SpriteMap(self.image, 16, 16)
        # self.sprite.add('IDLE', [0], origin=os)

        # self.sprite.play('IDLE')

    def render(self):
        peachy.graphics.set_color(0, 0, 255)
        peachy.graphics.draw_rect(self.x, self.y, 10, 10)
