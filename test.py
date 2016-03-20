import sys
from game import AgentObieEngine
from game.scenes import *
from game.worlds import *

if __name__ == "__main__":
    try:
        arg = sys.argv[1]
        name = sys.argv[2]
        
        game = AgentObieEngine(True)
        game.set_title('TEST ' + name)
        game.preload()

        if arg == '-D':
            world = game.change_world(GameWorld.NAME)
            world.change_scene(TestScene)
            world.scene.load_tmx('assets/' + name)

            try:
                px = int(sys.argv[3])
                py = int(sys.argv[4])
                world.scene.player.x = px
                world.scene.player.y = py
            except IndexError:
                pass

        elif arg == '-L':
            world = game.change_world(GameWorld.NAME)

            if name == 'LIGHT':
                world.change_scene(LightingScene)
            else:
                world.change_scene(TestScene)

        game.run()

    except IndexError:
        print('Invalid argument passed')
