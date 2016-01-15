import pygame
import os
import peachy
from peachy import PC
from game.levels import *

class GameWorld(peachy.World):
    NAME = 'game'

    STATE_PLAY = 'playing'
    STATE_PAUSED = 'paused'
    STATE_MESSAGE = 'message'

    def __init__(self):
        peachy.World.__init__(self, GameWorld.NAME)

        self.state = GameWorld.STATE_PLAY
        self.scene = None

        self.context = peachy.graphics.Surface((320, 240))

    def close(self):
        self.scene.exit()

    def play_scene(self, scene):
        self.scene = scene
        self.scene.load()

    def render(self):
        peachy.graphics.set_context(self.context)
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_rect(*self.context.get_rect())

        self.scene.render()

        if self.state == GameWorld.STATE_PAUSED:
            peachy.graphics.set_color(0, 0, 0)
            peachy.graphics.draw_rect(0, 0, PC.width / 2, 50)
            peachy.graphics.draw_rect(0, PC.height / 2 - 50, PC.width / 2, 50)

            peachy.graphics.set_color(255, 255, 255)
            peachy.graphics.draw_text('PAUSED', 136, 117)

        peachy.graphics.reset_context()
        peachy.graphics.draw_image(peachy.graphics.scale(self.context, 2), 0, 0)

        # Draw text after scaling has been done
        if self.state == GameWorld.STATE_MESSAGE:
            self.message.display()
        else:
            peachy.graphics.set_color(125, 125, 125)
            peachy.graphics.draw_text('AGENT OBIE | ALPHA 1', 0, 0)

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

