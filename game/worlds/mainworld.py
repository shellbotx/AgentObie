import peachy
from peachy import PC
from peachy.utils import Input

NEW = 0
LOAD = 1
EXIT = 2

class MainWorld(peachy.World):

    NAME = 'main'

    def __init__(self):
        super(MainWorld, self).__init__(MainWorld.NAME)
        self.current_selection = 0
        self.selections = [ "PLAY GAME", "EXIT" ]

    def start_new(self):
        return

    def render(self):
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(0, 0, PC.width, PC.height)

        font = peachy.graphics.font()

        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_text("AGENT OBIE | ALPHA BUILD 3", 0, 100, center=True)

        for selection in xrange(len(self.selections)):
            text = self.selections[selection]
            text_width, _ = font.size(text)

            x = (PC.width / 2) - text_width / 2
            y = (PC.height / 2) + (selection * 24) + (PC.height / 7)

            peachy.graphics.set_color(255, 255, 255)
            if selection == self.current_selection:
                peachy.graphics.draw_rect(x - 16, y, text_width + 32, 16)
                peachy.graphics.set_color(0, 0, 0)
            peachy.graphics.draw_text(text, x, y)

    def update(self):
        if Input.pressed('up'):
            self.current_selection -= 1
        if Input.pressed('down'):
            self.current_selection += 1

        if self.current_selection < 0:
            self.current_selection = 0
        elif self.current_selection > 2:
            self.current_selection = 2

        if Input.pressed('enter'):
            if self.current_selection == NEW:
                w = PC.engine.change_world("game")
                w.init_new_game()
            elif self.current_selection == LOAD:
                PC.engine.change_world("game")
            elif self.current_selection == EXIT:
                PC.quit()
        if Input.pressed('escape'):
            PC.quit()
