import os

import peachy
import peachy.fs
import peachy.resources

from game import config
from game.worlds import CinemaWorld, GameWorld, MainWorld


RESOURCE_OUTLINE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'res', 'outline.json')


class AgentObieEngine(peachy.Engine):

    def __init__(self, debug=False):
        peachy.Engine.__init__(self,
                               (config.VIEW_WIDTH * config.INNER_SCALE,
                                config.VIEW_HEIGHT * config.INNER_SCALE),
                               'Agent Obie', debug=debug)

        self.add_world(MainWorld())
        self.add_world(GameWorld())
        self.add_world(CinemaWorld())

    def preload(self):
        # TODO loading screen
        self.resources = peachy.resources.ResourceManager()
        self.resources.bind_outline(RESOURCE_OUTLINE_PATH)
        self.resources.activate_bundle('BaseResources')

        peachy.graphics.set_font(
            self.resources.get_resource_by_name('DefaultFont'))

        # peachy.fs.load_image(
        #     'ObieSpritesheet',
        #     use_resource_directory('img/obie.png'))
        #
        # peachy.fs.load_image(
        #     'SoldierSpritesheet',
        #     use_resource_directory('img/soldier.png'))
        #
        # peachy.fs.load_sound(
        #     'FootstepSound',
        #     use_resource_directory('snd/footsteps.wav'))

        # Create Obie sprite
        os = (4, 4)  # origin_standard
        oc = (4, 8)  # origin_crouch
        obie_sprite = peachy.graphics.SpriteMap(
            self.resources.get_resource_by_name('ObieSpritesheet'), 16, 16)

        obie_sprite.add('IDLE',
                        [0, 0, 0, 1, 2, 1, 0, 0, 0],
                        10, True, origin=os)
        obie_sprite.add('CLIMB_LADDER',
                        [40, 41, 42, 43], 15, True, True, origin=os)
        obie_sprite.add('CRAWL', [20, 21, 22, 23, 24, 25], 5, True, origin=oc)
        obie_sprite.add('CROUCH', [20], origin=oc)
        obie_sprite.add('FALL', [4], origin=os)
        obie_sprite.add('JUMP', [19], origin=os)
        obie_sprite.add('HANG', [5], origin=(4, 0))
        obie_sprite.add('PUSH', [6], origin=os)
        obie_sprite.add('RUN',
                        [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                        4, True, origin=os)
        obie_sprite.add('HIDDEN', [9], origin=os)
        obie_sprite.add('INVISIBLE', [50], origin=os)
        obie_sprite.add('INVISIBLE_RUN',
                        [60, 61, 62, 63, 64, 65, 66, 67, 68, 69],
                        4, True, origin=os)

        # Add ObieSprite to resource manager.
        obie_sprite_resource = peachy.resources.Resource(
            'ObieSprite', obie_sprite, '')
        self.resources.add_resource(obie_sprite_resource)
