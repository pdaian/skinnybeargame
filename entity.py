from settings import *
from pygame._sdl2 import Texture, Image

class BaseEntity(pg.sprite.Sprite):
    def __init__(self, app, name, collision):
        self.app = app
        self.name = name
        self.group = app.main_group
        super().__init__(self.group)

        self.attrs = ENTITY_SPRITE_ATTRS[name]
        entity_cache = self.app.cache.entity_sprite_cache
        self.all_states = entity_cache[name]['all_states']
        self.images = self.all_states['default']
        self.mask = entity_cache[name]['mask']
        self.rect = self.images[0].get_rect()

        # upload all computed surfaces into gpu memory
        # todo optimize this by doing surface computations in-gpu
        for state in self.all_states.keys():
            for image_index in range(len(self.all_states[state])):
                if not isinstance(self.all_states[state][image_index], Image):
                    # upload image to gpu as texture if not already done in cache
                    self.all_states[state][image_index] = Image(Texture.from_surface(self.app.renderer, self.all_states[state][image_index]), srcrect=self.rect)

        self.images = self.all_states['default']
        self.image = self.images[0]
        self.frame_index = 0
        self.deferred_updates = 0
        self.health = entity_cache[name]['health']
        if collision:
            self.app.collision_group.add(self)
        self.velocity = None
        self.does_damage = False


    def animate(self):
        if self.app.anim_trigger:
            self.frame_index = (self.frame_index + 1) % len(self.images)
            self.image = self.images[self.frame_index]

    def update(self):
        self.animate()
        pass


class Entity(BaseEntity):
    def __init__(self, app, name, pos, collision):
        super().__init__(app, name, collision)
        self.pos = vec2(pos) * TILE_SIZE
        self.player = app.player
        self.y_offset = vec2(0, self.attrs['y_offset'])
        self.screen_pos = vec2(0)

    def update(self):
        super().update()
        self.transform()
        if self.velocity is not None:
            self.move()
        self.set_rect()
        if self.deferred_updates % 50 == 0:
            self.change_layer()
            self.deferred_updates = 0
        self.deferred_updates += 1

    def move(self):
        self.pos += self.velocity.rotate_rad(-self.player.angle)

    def transform(self):
        pos = self.pos - self.player.offset
        pos = pos.rotate_rad(self.player.angle)
        self.screen_pos = pos + CENTER

    def change_layer(self):
        try:
            self.group.change_layer(self, self.screen_pos.y)
        except:
            print("layer change error", self.name, self.pos)

    def set_rect(self):
        self.rect.center = self.screen_pos + self.y_offset
