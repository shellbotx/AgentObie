import sys
from peachy import PC

from game import AgentObieEngine
from game.scenes import *
from game.worlds import *

def init(test_name):
    AgentObieEngine(True)
    PC.set_title('TEST ' + test_name)

if __name__ == "__main__":
    try:
        arg = sys.argv[1]
        name = sys.argv[2]
        
        AgentObieEngine(True)
        PC.set_title('TEST ' + name)

        if arg == '-D':
            PC.engine.change_world(GameWorld.NAME)
            PC.world.play_scene(TestScene)
            PC.world.scene.load_tmx('assets/' + name)

        elif arg == '-L':
            PC.engine.change_world(GameWorld.NAME)

            if name == 'LIGHT':
                PC.world.play_scene(LightingScene)
            else:
                PC.world.play_scene(TestScene)

        PC.engine.run()

    except IndexError:
        print 'Invalid argument passed'
