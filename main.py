import sys
from game import AgentObieEngine

try:
    import peachy
except ImportError:
    sys.path.append("C:/Users/Sheldon/Dropbox/Projects/Peachy")
    print("Peachy appened to system path.")
    import peachy

if __name__ == "__main__":
    debug = False

    try:
        if sys.argv[1] == '-D':
            debug = True
    except IndexError:
        pass

    game = AgentObieEngine(debug)
    game.run()
