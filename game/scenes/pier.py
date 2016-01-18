from game.scenes import AgentObieScene
from game.entities import Player, Lift

class PierScene(AgentObieScene):

    def __init__(self, world):
        super(PierScene, self).__init__(world)

    def load(self):
        self.player = Player(80, 200)
        self.load_tmx('assets/pier_01.tmx')

    def load_stage_OBJ(self, OBJ, stage, previous_stage):
        if OBJ.name == 'CARGO_LIFT':
            # TODO load custom image for cargo lift
            start_x = OBJ.x
            start_y = OBJ.y

            movement = OBJ.polygon_points[1]
            end_x = OBJ.x + movement[0]
            end_y = OBJ.y + movement[1]

            lift = Lift(start_x, start_y, end_x, end_y)
            lift.width = 56
            lift.height = 32

            return lift
        else:
            return super(PierScene, self).load_stage_OBJ(OBJ, stage, previous_stage)

