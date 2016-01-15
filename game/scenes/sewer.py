from scenes import AgentObieScene

class SewerScene(AgentObieScene):
    
    def __init__(self, world):
        AgentObieScene.__init__(self, world)
        self.world = world

    def load(self):
        self.player = Player(152, 0)
        self.load_stage('assets/sewer_01.tmx')
