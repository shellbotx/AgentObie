import peachy
import peachy.geo


class Lift(peachy.Entity):

    SPEED = 0.25


class AutoLift(peachy.Entity):
    """ Automatic Lifts move automatically """
    x = 0  # placeholder


class ManualLift(peachy.Entity, peachy.geo.Rect):
    """ Controlled Lifts wait for player input before moving """

    def __init__(self, nodes, width, height):
        node = nodes[0]

        super().__init__()
        peachy.geo.Rect.__init__(self, node.x, node.y, width, height)
        self.group = 'opaque'

        self.nodes = nodes
        self.current_node = 0

        self.solid = True

    def advance(self):
        target = self.nodes[self.current_node]
        if self.x == target.x and self.y == target.y:
            self.current_node += 1
            if self.current_node >= len(self.nodes):
                self.current_node = 0
        else:
            self.revert()

    def revert(self):
        self.current_node -= 1
        if self.current_node < 0:
            self.current_node = len(self.nodes) - 1

    def render(self):
        peachy.graphics.set_color(255, 0, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        target = self.nodes[self.current_node]

        if self.x != target.x or self.y != target.y:
            temp_x = self.x
            temp_y = self.y

            if temp_x > target.x:
                temp_x -= Lift.SPEED
            elif temp_x < target.x:
                temp_x += Lift.SPEED

            if temp_y > target.y:
                temp_y -= Lift.SPEED
            elif temp_y < target.y:
                temp_y += Lift.SPEED

            delta_x = self.x - temp_x
            delta_y = self.y - temp_y

            if delta_y < 0:
                passengers = self.collides_group('liftable', temp_x, self.y - 1)
            else:
                passengers = self.collides_group('liftable', temp_x, temp_y)
            for passenger in passengers:
                passenger.x -= delta_x
                passenger.y -= delta_y

            self.x = temp_x
            self.y = temp_y
