import sys
from peachy import PC
from game import AgentObieEngine
from game.scenes.pier import PierScene

if __name__ == "__main__":
    debug = False

    try:
        if sys.argv[1] == '-D':
            debug = True
    except IndexError:
        pass

    game = AgentObieEngine(debug)
    game.world.play_scene(PierScene(game.world))
    game.run()
