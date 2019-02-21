import sys
from game.engine import AgentObieEngine


if __name__ == "__main__":
    debug = False

    try:
        if sys.argv[1] == '-D':
            debug = True
    except IndexError:
        pass

    game = AgentObieEngine(debug)
    game.run()
