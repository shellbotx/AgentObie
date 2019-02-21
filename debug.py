import cProfile
import sys
import traceback
from game.engine import AgentObieEngine
from game.rooms import tests
from game.scenes import TestScene
from game.worlds import GameWorld, MainWorld

options = {
    'player': '',  # Player location -> player=0,0
    'profile': 'off',
    'profile_file': 'profile.prof',
    'scale': '1',
    'scene': '',
    'stage': '',
    'test': '',
}


def start_debug():
    game = AgentObieEngine(debug=True)
    game.title = 'Agent Obie DEBUG'
    game.preload()
    world = game.change_world(GameWorld.NAME)

    if options['scale']:
        game.scale = int(options['scale'])

    if options['test']:
        load_room(world, options['test'])
    elif options['scene']:
        load_scene(world, options['scene'])
    elif options['stage']:
        load_stage(world, options['stage'])
    else:
        world = game.change_world(MainWorld.NAME)

    if options['player']:
        pos = tuple(map(int, options['player'].split(',')))
        world.room.player.x = pos[0]
        world.room.player.y = pos[1]

    game.run()


def load_room(world, test_name, *args, **kwargs):
    """
    Run a test room (specified in game.rooms.test)
    ex: test=GenericTest
    """
    world.change_room(tests.__dict__[test_name](world, *args, **kwargs))


def load_scene(world, scene_name):
    world.change_room(tests.GenericTest(world))
    world.play_scene(TestScene(world))


def load_stage(world, name):
    world.change_room(tests.GenericTest(world))

    try:
        world.room.load_tmx('game/res/stage/' + name)
    except Exception:
        print("[ERROR] Could not parse {}".format(name))
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # debug test=BackgroundTest profile=on
    # debug profile=on
    # debug stage=pier_01.tmx profile=on
    # profile=on

    for argv in sys.argv:
        try:
            option, value = argv.split('=')
            assert options.get(option) is not None
            options[option] = value
        except ValueError:
            print(argv)
        except AssertionError:
            print("Invalid option: " + option)

    if options['profile'] in ['on', 'True']:
        cProfile.run('start_debug()', filename=options['profile_file'])
    else:
        start_debug()
