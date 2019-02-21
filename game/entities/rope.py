import peachy
import peachy.geo


class Rope(peachy.Entity, peachy.geo.Rect):

    STATE_ACTIVE = 0
    STATE_INACTIVE = 1

    def __init__(self, x, y, width, height, on_pull='', on_release='', down=''):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)
        self.group = 'interact rope'

        self.width = width
        self.height = height

        self.on_pull = on_pull
        self.on_release = on_release
        self.down = down

        self.handle = None
        self.visible = False

        self.state = Rope.STATE_INACTIVE

    def attach(self, player):
        self.state = Rope.STATE_ACTIVE
        if self.on_pull:
            exec(self.on_pull)

    def detach(self):
        self.state = Rope.STATE_INACTIVE
        if self.on_release:
            exec(self.on_release)

    def render(self):
        if self.state == Rope.STATE_INACTIVE:
            peachy.graphics.set_color(255, 0, 0)
        elif self.state == Rope.STATE_ACTIVE:
            peachy.graphics.set_color(0, 255, 0)
        peachy.graphics.draw_line(self.x, self.y,
                                  self.x + self.width, self.y + self.height)

    def update(self):
        if self.state == Rope.STATE_ACTIVE:
            if self.down:
                exec(self.down)

            self.state = Rope.STATE_INACTIVE

            handles = self.container.get_group('player')
            for handle in handles:
                try:
                    if self == handle.state_args['handle']:
                        self.state = Rope.STATE_ACTIVE
                        break
                except (KeyError, IndexError):
                    pass

            if self.state == Rope.STATE_INACTIVE:
                self.detach()
