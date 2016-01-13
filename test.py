import sys
from peachy import PC
from game import AgentObieEngine

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
            PC.engine.enter_level('TEST')
            PC.world.level.load_stage('assets/' + name)

        elif arg == '-S':
            PC.engine.play_scene(name)

        elif arg == '-L':
            PC.engine.enter_level(name)

        PC.engine.run()

    except IndexError:
        print 'Invalid argument passed'
