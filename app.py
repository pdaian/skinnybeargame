import sys
from settings import *
from cache import Cache
from player import Player
from scene import Scene
from pygame._sdl2 import Window, Renderer, Image, Texture
import random

class App:
    def __init__(self, cache=None):
        self.done = False
        pg.display.init()
        if cache is None:
            # SDL window setup code from https://github.com/pygame/pygame/issues/3575
            flags = pg.SCALED

            # create the display in "hidden" mode, because it isn't properly sized yet
            pg.display.set_mode((640,360), flags | pg.HIDDEN)

            # choose the initial scale factor for the window
            initial_scale_factor = 2.5  # <-- adjustable
            window = Window("sb and the power of <3", size=RES)
            window.size = (640 * initial_scale_factor, 360 * initial_scale_factor)
            window.position = pg._sdl2.WINDOWPOS_CENTERED
            self.window = window
            self.renderer = Renderer(window)
            self.generation = 0
        else:
            self.generation += 1
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0.01
        self.anim_trigger = False
        self.anim_event = pg.USEREVENT + 0
        pg.time.set_timer(self.anim_event, 100)
        # groups
        self.main_group = pg.sprite.LayeredUpdates()
        self.collision_group = pg.sprite.Group()
        self.transparent_objects = []
        # game objects
        self.cache = cache
        if cache is None:
            self.cache = Cache()
        self.player = Player(self)
        self.scene = Scene(self)

    def update(self):
        self.scene.update()
        self.main_group.update()
        pg.display.set_caption(f'{self.clock.get_fps(): .1f}')
        self.delta_time = self.clock.tick()

    def draw(self):
        # render scene tree
        if random.random() < .01:
            self.window.title = str(f"sb and the power of <3 | FPS: {int(self.clock.get_fps())}")
        if self.player.health > 0:
            self.renderer.clear()
            self.renderer.draw_color = (107, 142, 35, 255)
            self.main_group.draw(self.renderer)
            font = pg.font.Font("assets/fonts/yarn.ttf", size=100)
            text = font.render("Yarn: %3d%%" % (self.player.health), 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            text_image = Texture.from_surface(self.renderer, text)
            self.renderer.blit(text_image, pg.Rect(0, 0, text_image.width, text_image.height))
            self.renderer.present()
        else:
            self.renderer.clear()
            self.renderer.draw_color = (64, 48, 27, 255)
            font = pg.font.Font("assets/fonts/yarn.ttf", size=100)
            text = font.render("skinny bear has run out of yarn", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            text_image = Texture.from_surface(self.renderer, text)
            self.renderer.blit(text_image, pg.Rect(50, H_HEIGHT-300, text_image.width, text_image.height))
            text = font.render("this kills the skinny bear :(", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            text_image = Texture.from_surface(self.renderer, text)
            self.renderer.blit(text_image, pg.Rect(50, H_HEIGHT-200, text_image.width, text_image.height))
            text = font.render("ESC - restart", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            text_image = Texture.from_surface(self.renderer, text)
            self.renderer.blit(text_image, pg.Rect(50, H_HEIGHT+100, text_image.width, text_image.height))
            self.renderer.present()

    def check_events(self):
        self.anim_trigger = False
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                self.done = True
                self.__init__(cache=self.cache)
            elif e.type == self.anim_event:
                self.anim_trigger = True
            elif e.type == pg.KEYDOWN:
                self.player.single_fire(event=e)

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):
        while not self.done:
            self.get_time()
            self.update()
            self.draw()
            self.check_events()

