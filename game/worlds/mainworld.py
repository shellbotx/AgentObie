import peachy
from peachy import PC
from peachy.utils import Key

PLAY = 0
EXIT = 1


class MainWorld(peachy.World):

    NAME = 'main'

    def __init__(self):
        super(MainWorld, self).__init__(MainWorld.NAME)
        self.current_selection = 0
        self.selections = ["PLAY", "EXIT"]

    def start_new(self):
        return

    def render(self):
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(0, 0, PC().canvas_width, PC().canvas_height)

        font = peachy.graphics.font()
        x_align = 64

        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_text("AGENT OBIE", x_align, 150)
        peachy.graphics.draw_text("ALPHA - BUILD 4", x_align, 166)

        highlight_width = 0
        for selection in range(len(self.selections)):
            text = self.selections[selection]
            _, _, text_width, text_height = font.get_rect(text)
            if text_width + 8 > highlight_width:
                highlight_width = text_width + 8

        for selection in range(len(self.selections)):
            text = self.selections[selection]
            # _, _, text_width, text_height = font.get_rect(text)

            y = (PC().canvas_height / 2) + (selection * 24)

            peachy.graphics.set_color(255, 255, 255)
            if selection == self.current_selection:
                peachy.graphics.draw_rect(x_align - 4, y - 2,
                                          highlight_width, text_height + 6)
                peachy.graphics.set_color(0, 0, 0)
            peachy.graphics.draw_text(text, x_align, y)

    def update(self):
        if Key.pressed('F1'):
            PC().toggle_fullscreen()
        if Key.pressed('up'):
            self.current_selection -= 1
        if Key.pressed('down'):
            self.current_selection += 1

        if self.current_selection < 0:
            self.current_selection = 0
        elif self.current_selection > 2:
            self.current_selection = 2

        if Key.pressed('enter'):
            if self.current_selection == PLAY:
                w = PC().change_world("game")
                w.init_new_game()
            elif self.current_selection == EXIT:
                PC().quit()
        if Key.pressed('escape'):
            PC().quit()
