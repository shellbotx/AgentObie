import peachy

from game import config
from game.scenes.actors import Actor, Message


def wait(time):
    """ Locks scene until the specified amount of time has passed. """
    time = int((time / 1000) * peachy.PC().fps)
    while time > 0:
        time -= 1
        yield False
    yield True


def wait_for_actor(actor):
    """ Locks scene until actor has returned to idle state. """
    while actor.state != Actor.STATE_IDLE:
        yield False
    yield True


def wait_for_input():
    """ Locks scene until <space> is pressed by user. """
    while not peachy.utils.Key.pressed('space'):
        yield False
    yield True


def wait_for_message(message):
    """ Locks scene until message is completed. """
    while message.typing:
        yield False
    yield True


class Scene(object):
    STATE_READY = 'ready'
    STATE_WAITING = 'wait'

    def __init__(self, world):
        self.world = world
        self.room = world.room

        self.actors = []
        self.messages = []

        self.backgrounds = []
        self.foregrounds = []

        self.subcontext = peachy.graphics.Surface((320, 240))
        self.subcontext_rect = self.subcontext.get_rect()

        self.phase = self.advance()

    def exit(self):
        self.world.end_scene()

    def render(self):
        peachy.graphics.push_context(self.subcontext)  # Open scale
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(*self.subcontext_rect)

        for background in self.backgrounds:
            background.render()

        for actor in self.actors:
            actor.render()

        for foreground in self.foregrounds:
            foreground.render()

        for message in self.messages:
            message.render()

        peachy.graphics.reset_context()     # Close scale
        peachy.graphics.scale(self.subcontext, config.INNER_SCALE,
                              peachy.graphics._context)

        for message in self.messages:
            message.render_text()

    def update(self):
        for actor in self.actors:
            actor.update()

        for message in self.messages:
            message.update()

        try:
            next(self.phase)
        except StopIteration:
            self.exit()

    def advance(self):
        yield False


from game.scenes.test_scene import TestScene
