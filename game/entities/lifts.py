import peachy

class Lift(peachy.Entity):

    SPEED = 0.25
    
'''
    def __init__(self, start, end):
        peachy.Entity.__init__(self, start.x, start.y)

        self.dest1 = start
        self.dest2 = end

        self.target = None

        self.width = 8
        self.height = 4
        self.solid = True

    def toggle(self):
        target = (self.target_x, self.target_y)

        dest = None
        if target != self.dest1:
            dest = self.dest1
        else:
            dest = self.dest2

        self.target_x, self.target_y = dest

    def render(self):
        peachy.graphics.set_color(255, 0, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.x != self.target_x or self.y != self.target_y:
            temp_x = self.x
            temp_y = self.y
            
            if temp_y > self.target_y:
                temp_y -= Lift.SPEED
            elif temp_y < self.target_y:
                temp_y += Lift.SPEED

            delta_x = self.x - temp_x
            delta_y = self.y - temp_y

            passengers = self.collides_group('liftable', temp_x, temp_y)
            for passenger in passengers:
                passenger.x -= delta_x
                passenger.y -= delta_y

            self.x = temp_x
            self.y = temp_y
'''

# class AutomaticLift(peachy.Entity):
#     """ Automatic Lifts move automatically """

class ControlledLift(peachy.Entity):
    """ Controlled Lifts wait for player input before moving """

    def __init__(self, nodes, width, height):
        node = nodes[0]

        super(ControlledLift, self).__init__(node.x, node.y)

        self.nodes = nodes
        self.current_node = 0

        self.width = width
        self.height = height
        self.solid = True

    def advance(self):
        target = self.nodes[self.current_node]
        if self.x == target.x and self.y == target.y:
            self.current_node += 1
            if self.current_node >= len(self.nodes):
                self.current_node = 0

    def render(self):
        peachy.graphics.set_color(255, 0, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        target = self.nodes[self.current_node]

        if self.x != target.x or self.y != target.y:
            temp_x = self.x
            temp_y = self.y
            
            if temp_y > target.y:
                temp_y -= Lift.SPEED
            elif temp_y < target.y:
                temp_y += Lift.SPEED

            delta_x = self.x - temp_x
            delta_y = self.y - temp_y

            passengers = self.collides_group('liftable', temp_x, temp_y)
            for passenger in passengers:
                passenger.x -= delta_x
                passenger.y -= delta_y

            self.x = temp_x
            self.y = temp_y
