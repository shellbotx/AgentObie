import sys
from peachy import PC
from game import AgentObieEngine

if __name__ == "__main__":
    debug = False

    try:
        if sys.argv[1] == '-D':
            debug = True
    except IndexError:
        pass

    game = AgentObieEngine(debug)
    game.world.change_level('LEVEL_01')
    game.run()
