from peachy import PC

from game.scenes import Message, Scene, \
    wait, wait_for_actor, wait_for_input, wait_for_message
from game.scenes.actors import Obie


class TestScene(Scene):

    def __init__(self, world):
        super().__init__(world)

    def advance(self):
        # Create actors
        obie = Obie(50, PC().canvas_width / 4)
        obie.sprite.play('RUN')
        message = Message([
            "Looks like Agent Obie will have dialogue...",
            "How exciting!"],
            obie.x - 16, 42, obie)

        self.actors.append(obie)  # Show actor
        yield from wait_for_input()

        dx = message.x + Message.BOX_WIDTH - 16
        obie.move_to(dx, obie.y, 2000)
        message.move_to(dx - Message.BOX_WIDTH / 2, message.y, 2000)

        self.messages.append(message)  # Show message
        yield from wait_for_message(message)
        yield from wait_for_actor(obie)
        yield from wait_for_input()

        self.messages.remove(message)
        obie.move_to(PC().canvas_width / 2, obie.y, 1500)
        yield from wait_for_actor(obie)
        yield from wait(1000)
        yield
