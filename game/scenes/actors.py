import peachy
from peachy.utils import Counter
from peachy.geo import Point


def milliseconds_to_frames(milli):
    return int((milli / 1000) * peachy.PC().fps)


class Actor(peachy.Entity):
    """ Actors are controlled by Scenes. They contain no user input and only follow
    stage directions. """

    STATE_IDLE = 0
    STATE_MOVING = 1

    def __init__(self, x, y):
        super().__init__(x, y)
        self.state = Actor.STATE_IDLE

    def move_to(self, dx, dy, duration=0):
        # duration in milliseconds
        if self.x == dx and self.y == dy:
            return

        duration = milliseconds_to_frames(duration)

        if duration == 0:
            self.x = dx
            self.y = dy
        else:
            self.state = Actor.STATE_MOVING
            self.start = Point(self.x, self.y)
            self.destination = Point(dx, dy)
            self.duration = duration
            self.elapsed = 0

    def update(self):
        if self.state == Actor.STATE_MOVING:
            self.elapsed += 1

            ratio = self.elapsed / self.duration
            dx = self.destination.x - self.start.x
            dy = self.destination.y - self.start.y

            self.x = self.start.x + dx * ratio
            self.y = self.start.y + dy * ratio

            if (self.x, self.y) == self.destination:
                self.state = Actor.STATE_IDLE


class Message(Actor):

    BOX_WIDTH = 120
    BOX_HEIGHT = 50

    def __init__(self, text, x, y, speaker=None, text_speed=2):
        super().__init__(x, y)
        if isinstance(text, list):
            self.messages = text
        else:
            self.messages = [text]

        self.current_message = 0
        self.speaker = speaker

        self.delay = Counter(0, text_speed)
        self.index = Counter(0, len(self.messages[self.current_message]))
        self.typing = True

    def next_message(self):
        self.current_message += 1
        self.delay.reset()
        self.index.reset()
        self.index.target = len(self.messages[self.current_message])

    def render(self):
        # Draw text box
        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_rounded_rect(self.x, self.y, Message.BOX_WIDTH,
                                          Message.BOX_HEIGHT, 0.2)
        # Draw speaker indicator
        if self.speaker:
            points = []
            points.append((self.speaker.x - 4, self.y + Message.BOX_HEIGHT))
            points.append((self.speaker.x + 4, self.y + Message.BOX_HEIGHT))
            points.append((self.speaker.x, self.y + Message.BOX_HEIGHT + 6))
            peachy.graphics.draw_polygon(points, aa=True)

    def render_text(self):
        # Note: called outside of scale context, therefore all coordinates
        # should be scaled by 2x.

        text = self.messages[self.current_message][:self.index.current]

        # Fit font inside of messagebox
        font = peachy.fs.resources["DefaultFont"]
        _, _, fw, _ = font.get_rect('_')
        fh = font.height / 100

        lines = []
        if (len(text) * fw) / 2 > Message.BOX_WIDTH - 16:
            words = text.split(' ')
            line = ''
            for word in words:
                line_length = ((len(word) + 1) * fw + len(line) * fw) / 2
                if line_length > Message.BOX_WIDTH - 16:
                    lines.append(line)
                    line = word + ' '
                else:
                    line += word + ' '
            lines.append(line)
        else:
            lines = [text]

        peachy.graphics.set_color(50, 50, 50)
        for i in range(len(lines)):
            line = lines[i]
            peachy.graphics.draw_text(line,
                                      self.x * 2 + 8,
                                      self.y * 2 + 8 + fh * 2 * i)

    def update(self):
        if self.typing:
            if self.delay.tick():
                if self.index.tick():
                    if self.current_message == len(self.messages) - 1:
                        self.typing = False
                    elif peachy.utils.Key.pressed('space'):
                            self.next_message()
                else:
                    self.delay.reset()
            elif peachy.utils.Key.pressed('space'):
                self.index.complete()
                self.delay.complete()
        super().update()


class Obie(Actor):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sprite = peachy.fs.resources['ObieSprite']
        self.sprite.play('IDLE')

    def render(self):
        # peachy.graphics.draw(self.sprite, self.x, self.y)
        self.sprite.render(self.x, self.y)
