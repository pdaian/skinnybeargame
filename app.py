from settings import *
from cache import Cache
from player import Player
from scene import Scene
import time
from pygame._sdl2 import Window, Renderer, Image, Texture
import threading

class App:
    def __init__(self, cache=None):
        self.done = False
        pg.display.init()
        self.screen = pg.display.set_mode(RES)
        self.window = Window("sb and the power of <3", resizable=False, size=RES)
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
        self.start = time.time()
        self.end = 0
        self.render_lock = threading.Lock()

    def run(self):
        while not self.done:
            self.render_lock.acquire()
            # Check Events
            self.anim_trigger = False
            for e in pg.event.get():
                if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                    self.done = True
                    pg.quit()
                    #sys.exit()
                elif e.type == self.anim_event:
                    self.anim_trigger = True
                elif e.type == pg.KEYDOWN and (self.player.health < 1 and e.key == pg.K_SPACE):
                    self.__init__(cache=self.cache)
                    self.player.single_fire(event=e)
                elif e.type == pg.KEYDOWN:
                    self.player.single_fire(event=e)

            # Update Time
            self.time = pg.time.get_ticks() * 0.001

            # Update Frame
            self.scene.update()
            self.main_group.update()
            pg.display.set_caption(f'{self.clock.get_fps(): .1f}')
            self.delta_time = self.clock.tick()

            # Draw / render scene tree
            self.renderer.clear()
            if self.player.health > 0:
                self.renderer.draw_color = (107, 142, 35, 255)
                self.main_group.draw(self.renderer)
                font = pg.font.Font("assets/fonts/yarn.ttf", size=100)
                text = font.render("Yarn: %3d%%" % (self.player.health), 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
                text_image = Image(Texture.from_surface(self.renderer, text))
                Image(Texture.from_surface(self.renderer, text)).draw(dstrect=(WIDTH-500, 10))

                chat = self.SUAVE.get_recent_chat_messages()

            else:
                if self.end == 0:
                    self.end = time.time()
                #self.done = True
                self.renderer.draw_color = (64,48,27, 255)
                font = pg.font.Font("assets/fonts/yarn.ttf", size=100)
                text = font.render("skinny bear has run out of yarn", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
                Image(Texture.from_surface(self.renderer, text)).draw(dstrect=(200, H_HEIGHT-300))
                text = font.render("this kills the bear :(", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
                Image(Texture.from_surface(self.renderer, text)).draw(dstrect=(200, H_HEIGHT-200))
                text = font.render("SPACE - restart esc - give up", 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
                Image(Texture.from_surface(self.renderer, text)).draw(dstrect=(200, H_HEIGHT+100))
                high_score = int(open('hs').read().strip())
                score = int(self.end - self.start)
                if score > high_score:
                    open('hs', 'w').write(str(score))
                text = font.render("score: %d highest ever score: %d" % (score, high_score), 1, (222,20,20)) # Arguments are: text, anti-aliasing, color
                Image(Texture.from_surface(self.renderer, text)).draw(dstrect=(200, H_HEIGHT+200))
            self.renderer.present()
            self.window.title = str(f"FPS: {self.clock.get_fps()}")

            self.render_lock.release()

            # todo exception handle these calls gracefully
