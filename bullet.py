from entity import *


class Explosion(Entity):
    def __init__(self, app, name='explosion', pos=(0, 0)):
        super().__init__(app, name, pos, False)
        self.life_time_cycles = self.attrs['num_layers'] - 1
        self.cycles = 0
        self.transform()
        self.update()

    def update(self):
        super().update()
        self.check_life_time()

    def change_layer(self):
        self.group.change_layer(self, self.rect.centery)

    def check_life_time(self):
        if self.app.anim_trigger:
            self.cycles += 1
            if self.cycles > self.life_time_cycles:
                self.kill()


class Bullet(BaseEntity):
    def __init__(self, app, name='bullet', pos=(0, 0)):
        super().__init__(app, name, False)
        self.pos = vec2((pos[0] + 10, pos[1]))
        self.player = app.player
        self.y_offset = self.attrs['y_offset']

        self.speed = 0
        self.speed = 0.7
        self.bullet_direction = vec2(self.speed * self.player.last_direction_mult[0], self.speed * self.player.last_direction_mult[1])
        self.life_time_cycles = 20
        self.cycles = 0
        #self.angle = 90
        self.angle = self.player.angle

    def check_collision(self):
        hits = pg.sprite.spritecollide(self, self.app.collision_group,
                                      dokill=False, collided=pg.sprite.collide_mask)
        if hits:
            sprite_hit = hits[0]
            if sprite_hit.health is not None:
                sprite_hit.health -= 1
            if sprite_hit.health == 0:
                sprite_hit.kill()
                Explosion(self.app, name="objectexplosion", pos=sprite_hit.pos/TILE_SIZE) 
            Explosion(self.app, pos=(self.pos + self.player.offset) / TILE_SIZE)
            self.kill()

    def change_layer(self):
        self.group.change_layer(self, self.rect.centery - self.y_offset)

    def load_images(self):
        return self.app.cache.cached_entity_data[self.name]

    def check_life_time(self):
        if self.app.anim_trigger:
            self.cycles += 1
            if self.cycles > self.life_time_cycles:
                self.kill()

    def update(self):
        self.run()
        self.rotate()
        self.change_layer()
        self.check_life_time()
        self.check_collision()

    def rotate(self):
        pos = self.pos
        new_pos = pos.rotate_rad(self.player.angle)
        self.rect.center = new_pos + CENTER
        self.rect.centery += self.y_offset

    def run(self):
        bullet_direction = self.bullet_direction * self.app.delta_time
        self.pos += bullet_direction.rotate_rad(-self.angle) - self.player.inc
