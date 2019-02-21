import peachy


class CinemaWorld(peachy.World):
    NAME = 'cinema'

    STATE_READY = 'ready'
    STATE_WAITING = 'wait'

    def __init__(self):
        super().__init__(CinemaWorld.NAME)
        self.scene = None

        self.actors = []
        self.directions = []

        self.stage = []
        self.background = []
        self.foreground = []

        self.subcontext = peachy.graphics.Surface((320, 240))
        self.subcontext_rect = self.subcontext.get_rect()

        self.active_messages = []
        self.current_directions = None

    def load_script(self):
        return

    def render(self):
        peachy.graphics.set_context(self.subcontext)  # Open scale
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(*self.subcontext_rect)

        for background in self.backgrounds:
            background.render()

        for actor in self.actors:
            actor.render()

        for foreground in self.foregrounds:
            foreground.render()

        peachy.graphics.reset_context()     # Close scale
        peachy.graphics.draw(peachy.graphics.scale(self.subcontext, 2), 0, 0)

        for message in self.active_messages:
            message.render()

    def update(self):
        if peachy.utils.Key.pressed('space'):
            if self.current_direction.can_advance:
                self.current_direction.advance()
