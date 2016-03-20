import os
import peachy
from peachy import PC
from game.scenes import *
from game.utility import draw_message

class GameWorld(peachy.World):
    NAME = 'game'

    STATE_PLAY = 'playing'
    STATE_PAUSED = 'paused'
    STATE_MESSAGE = 'message'
    STATE_GAMEOVER = 'game-over'

    def __init__(self):
        super(GameWorld, self).__init__(GameWorld.NAME)

        self.state = GameWorld.STATE_PLAY
        # self.scene = None

        self.context = peachy.graphics.Surface((320, 240))

    def init_new_game(self):
        self.change_scene(PierScene)

    def close(self):
        self.scene.clear()

    def change_scene(self, scene):
        if self.scene:
            self.scene.clear()
        self.scene = scene(self)
        self.scene.load()

    def render(self):
        peachy.graphics.set_context(self.context)  # Open scale
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(*self.context.get_rect())

        self.scene.render()

        if self.state == GameWorld.STATE_PAUSED:
            peachy.graphics.set_color(0, 0, 0)
            peachy.graphics.draw_rect(0, 0, PC.width / 2, 50)
            peachy.graphics.draw_rect(0, PC.height / 2 - 50, PC.width / 2, 50)


        peachy.graphics.reset_context()     # Close scale
        peachy.graphics.draw(peachy.graphics.scale(self.context, 2), 0, 0)

        # Draw text after scaling has been done
        if self.state == GameWorld.STATE_PAUSED:
            peachy.graphics.set_color(255, 255, 255)
            peachy.graphics.draw_text('PAUSE', 136, 117, font=peachy.fs.resources['FiraMono'])
        if self.state == GameWorld.STATE_MESSAGE:
            draw_message(self.scene.player, self.message.message)
        elif self.state == GameWorld.STATE_GAMEOVER:
            draw_message(self.scene.player, "Game Over ... press <SPACE> to continue")
        else:
            peachy.graphics.set_color(125, 125, 125)
            peachy.graphics.draw_text('AGENT OBIE | ALPHA 4', 0, 0)
            self.scene.draw_HUD()

    def update(self):
        if peachy.utils.Input.pressed('escape'):
            PC.quit()
        if peachy.utils.Input.pressed('F1'):
            PC.engine.fullscreen()

        if self.state == GameWorld.STATE_PLAY:
            self.scene.update()

            if peachy.utils.Input.pressed('p'):
                self.state = GameWorld.STATE_PAUSED
        elif self.state == GameWorld.STATE_PAUSED:
            if peachy.utils.Input.pressed('p'):
                self.state = GameWorld.STATE_PLAY
        elif self.state == GameWorld.STATE_MESSAGE:
            if peachy.utils.Input.pressed('space'):
                self.message.destroy()
                self.state = GameWorld.STATE_PLAY
        elif self.state == GameWorld.STATE_GAMEOVER:
            if peachy.utils.Input.pressed('space'):
                self.scene.reload_stage()
                self.state = GameWorld.STATE_PLAY
