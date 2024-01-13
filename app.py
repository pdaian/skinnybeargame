import sys
from settings import *
from cache import Cache
from player import Player
from scene import Scene
from pygame._sdl2 import Window, Renderer

class App:
    def __init__(self, cache=None):
        pg.display.init()
        self.screen = pg.display.set_mode(RES)
        self.window = Window("sb and the power of <3", resizable=True)
        self.renderer = Renderer(self.window)
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
        self.done = False

    def update(self):
        self.scene.update()
        self.main_group.update()
        pg.display.set_caption(f'{self.clock.get_fps(): .1f}')
        self.delta_time = self.clock.tick()

    def draw(self):
        # render scene tree
        self.renderer.clear()
        self.main_group.draw(self.renderer)
        self.renderer.present()
        self.window.title = str(f"FPS: {self.clock.get_fps()}")
        return
        if self.player.health > 0:
            renderer.draw_color = (107, 142, 35, 255)
            self.main_group.draw(self.screen)
            background_rect = pg.Surface((550,150))  # the size of your rect
            background_rect.set_alpha(200)                # alpha level
            background_rect.fill((64,48,27))           # this fills the entire surface
            self.screen.blit(background_rect, (WIDTH-550, 0))
            font = pg.font.Font("assets/fonts/yarn.ttf", size=100)
            text = font.render("Yarn: %3d%%" % (self.player.health), 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            self.screen.blit(text, (WIDTH-500, 10))
            pg.display.flip()
        else:
            #self.done = True
            self.screen.fill((64,48,27))
            font = pg.font.Font("assets/fonts/yarn.ttf", size=100)
            text = font.render("skinny bear has run out of yarn", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            self.screen.blit(text, (200, H_HEIGHT-300))
            text = font.render("this kills the skinny bear :(", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            self.screen.blit(text, (200, H_HEIGHT-200))
            text = font.render("SPACE - restart esc - give up", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
            self.screen.blit(text, (200, H_HEIGHT+100))
            pg.display.flip()
            

    def check_events(self):
        self.anim_trigger = False
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                self.done = True
                #pg.quit()
                #sys.exit()
            elif e.type == self.anim_event:
                self.anim_trigger = True
            elif e.type == pg.KEYDOWN and (self.player.health < 1 and e.key == pg.K_SPACE):
                self.__init__(cache=self.cache)
                self.player.single_fire(event=e)
            elif e.type == pg.KEYDOWN:
                self.player.single_fire(event=e)


    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):
        while not self.done:
            self.check_events()
            self.get_time()
            self.update()
            self.draw()

