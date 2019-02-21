import os
import peachy
from peachy import PC

from game import config
from game.entities import Player
from game.rooms import Pier
from game.utility import CheckpointData, draw_message

STATE_MAIN = 'playing'   # STATE_MAIN / STATE_PLAY / STATE_PLAYING
STATE_PAUSED = 'paused'
STATE_MESSAGE = 'message'
STATE_CINEMA = 'cinema'
STATE_GAMEOVER = 'game-over'


class GameWorld(peachy.World):
    NAME = 'game'

    def __init__(self):
        super().__init__(GameWorld.NAME)

        self.add_state(GameWorld_MainState(self))
        self.add_state(GameWorld_CinemaState(self))
        self.add_state(GameWorld_GameOverState(self))
        self.add_state(GameWorld_MessageState(self))
        self.add_state(GameWorld_PauseState(self))

        self.room = None
        self.scene = None
        self.checkpoint = None

        self.subcontext = peachy.graphics.Surface((config.VIEW_WIDTH,
                                                   config.VIEW_HEIGHT))
        self.subcontext_rect = self.subcontext.get_rect()

    def init_new_game(self):
        self.change_room(Pier(self))

    def change_room(self, room):
        super().change_room(room)
        self.checkpoint = None

    def end_scene(self):
        self.scene = None
        self.change_state(STATE_MAIN)

    def play_scene(self, scene):
        self.scene = scene
        self.change_state(STATE_CINEMA)

    def render_HUD(self):
        player = self.room.player
        peachy.graphics.set_color(255, 255, 255)

        # Draw keys
        peachy.graphics.draw_text("KEYS: {0}".format(player.key_count), 0, 14)

        # Draw gadget detail
        if player.gadget.name != '':
            peachy.graphics.draw_text(player.gadget.name, 0, 28)

        # Draw gadget timer
        time = str(round(float(player.gadget.timer) / 60.0, 1))
        x = (player.x + player.width + 4) * config.INNER_SCALE
        y = (player.y + 4) * config.INNER_SCALE

        if player.gadget.state == 0:
            peachy.graphics.draw_text(time, x, y)
        elif player.gadget.state == 2:
            peachy.graphics.set_color(255, 255, 0)
            peachy.graphics.draw_text(time, x, y)

    def render_room(self):
        # Use a subcontext (for scaling)
        peachy.graphics.push_context(self.subcontext)
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(*self.subcontext_rect)

        # Draw room
        self.room.render()

        # Blit subcontext to main context
        peachy.graphics.reset_context()
        peachy.graphics.scale(self.subcontext, config.INNER_SCALE,
                              peachy.graphics._context)

    def respawn(self):
        if self.checkpoint:
            self.room.player.change_state(Player.STATE_STANDARD)
            self.room.player.change_gadget(self.checkpoint.gadget)
            self.room.load_tmx(self.checkpoint.stage, False, True)
        else:
            self.room.player.change_state(Player.STATE_STANDARD)
            self.room.load_tmx(
                os.path.basename(self.room.stage_data.path), True)
            self.room.player.change_gadget(self.room.starting_gadget)
        self.change_state(STATE_MAIN)

    def set_checkpoint(self):
        self.checkpoint = CheckpointData.generate(self.room)

    def update(self):
        if peachy.utils.Key.pressed('escape'):
            PC().quit()
        if peachy.utils.Key.pressed('F1'):
            PC().toggle_fullscreen()
        super().update()


class GameWorld_MainState(peachy.WorldState):

    def __init__(self, world):
        super().__init__(STATE_MAIN, world)

    def render(self):
        self.world.render_room()
        self.world.render_HUD()

    def update(self):
        self.world.room.update()
        if peachy.utils.Key.pressed('p'):
            self.world.change_state(STATE_PAUSED)


class GameWorld_CinemaState(peachy.WorldState):

    def __init__(self, world):
        super().__init__(STATE_CINEMA, world)

    def render(self):
        self.world.scene.render()

    def update(self):
        self.world.scene.update()


class GameWorld_GameOverState(peachy.WorldState):

    def __init__(self, world):
        super().__init__(STATE_GAMEOVER, world)

    def render(self):
        self.world.render_room()
        draw_message(self.world.room.player,
                     "Game Over ... press <SPACE> to continue")

    def update(self):
        if peachy.utils.Key.pressed('space'):
            self.respawn()


class GameWorld_MessageState(peachy.WorldState):

    def __init__(self, world):
        super().__init__(STATE_MESSAGE, world)
        self.handle = None

    def enter(self, previous_state, message):
        self.handle = message

    def render(self):
        self.world.render_room()
        draw_message(self.world.room.player, self.handle.message)

    def update(self):
        if peachy.utils.Key.pressed('space'):
            self.handle.destroy()
            self.world.change_state(STATE_MAIN)


class GameWorld_PauseState(peachy.WorldState):

    def __init__(self, world):
        super().__init__(STATE_PAUSED, world)
        self.selected = 0
        self.options = ['RESUME', 'OPTIONS', 'MAIN MENU', 'EXIT GAME']

    def enter(self, previous_state):
        self.world.room.pause()

    def exit(self, next):
        self.world.room.resume()
        self.selected = 0

    def render(self):
        self.world.render_room()
        draw_text = peachy.graphics.draw_text  # Because 80 line cap

        # Draw blur
        peachy.graphics.set_color(0, 0, 0, 125)
        peachy.graphics.draw_rect(0, 0, PC().canvas_width, PC().canvas_height)

        # Draw border
        border_height = PC().canvas_height / 8

        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(0, 0, PC().canvas_width, border_height)
        peachy.graphics.draw_rect(0, PC().canvas_height - border_height,
                                  PC().canvas_width, border_height)

        # Draw window
        pause_rect = Rect(PC().canvas_width / 3, PC().canvas_height / 3,
                          PC().canvas_width / 3, PC().canvas_height / 3)

        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(*pause_rect.ls())
        peachy.graphics.set_color(15, 56, 87)
        peachy.graphics.draw_rect(*pause_rect.ls(), thickness=2)

        # Draw information
        peachy.graphics.set_color(210, 210, 210)
        draw_text('||| PAUSE |||',
                  pause_rect.center_x,
                  pause_rect.y + 48,
                  center=True)

        peachy.graphics.set_color(125, 125, 125)
        draw_text(self.world.room.pause_menu_name,
                  pause_rect.center_x,
                  pause_rect.y + 84,
                  center=True)
        gadget_name = self.world.room.player.gadget.name
        if gadget_name == '':
            gadget_name = 'NONE'
        gadget_name = '%-6s' % gadget_name
        draw_text('GADGET ... ' + gadget_name,
                  pause_rect.center_x,
                  pause_rect.y + 100,
                  center=True)
        draw_text('  KEYS ... ' + '%-6s' %
                  str(self.world.room.player.key_count),
                  pause_rect.center_x,
                  pause_rect.y + 116,
                  center=True)

        # Draw options
        peachy.graphics.set_color(210, 210, 210)
        for i in range(0, len(self.options)):
            text = self.options[i]

            if i == self.selected:
                text = ' ' + text
                peachy.graphics.set_color(35, 76, 107)
            else:
                peachy.graphics.set_color(210, 210, 210)

            y = pause_rect.center_y + 8 + 24 * i
            draw_text(text, pause_rect.x + 48, y)

    def update(self):
        if peachy.utils.Key.pressed('p'):
            self.world.change_state(STATE_MAIN)
            self.world.room.resume()
        elif peachy.utils.Key.pressed('up'):
            if self.selected > 0:
                self.selected -= 1
        elif peachy.utils.Key.pressed('down'):
            if self.selected < len(self.options) - 1:
                self.selected += 1
        elif peachy.utils.Key.pressed('enter'):
            if self.selected == 0:  # Resume
                self.world.change_state(STATE_MAIN)
            elif self.selected == 1:  # Show options
                return
            elif self.selected == 2:  # Main Menu
                PC().change_world('main')
            elif self.selected == 3:  # Exit
                PC().quit()
