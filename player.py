from settings import *
import math
from entity import BaseEntity
from bullet import Bullet


class Player(BaseEntity):
    def __init__(self, app, name='player'):
        super().__init__(app, name, False)
        self.group.change_layer(self, CENTER.y)

        self.rect = self.image.get_rect(center=CENTER)

        self.offset = vec2(0)
        self.inc = vec2(0)
        self.prev_inc = vec2(0)
        self.angle = 0
        self.diag_move_corr = 1 / math.sqrt(2)
        self.last_direction_mult = vec2([1,0]) # multiplier for x bullet direction
        self.flipped_right = True
        self.walking = False
        self.animation = ""
        self.health = 100
        
    def start_walking(self):
        self.walking = True
        self.set_animation("walking")
        
    def stop_walking(self):
        self.walking = False
        self.set_animation("default")
        
    def set_animation(self, animation):
        entity_cache = self.app.cache.entity_sprite_cache
        self.animation = animation
        self.images = entity_cache[self.name]['additional_states'][animation]
        self.frame_index = 0
        self.app.anim_trigger = True
        
    def animate(self):
        super().animate()
        if self.app.anim_trigger:
            if not self.flipped_right:
                self.image = pg.transform.flip(self.image, True, False)

    def control(self):
        self.inc = vec2(0)
        speed = PLAYER_SPEED * self.app.delta_time
        rot_speed = PLAYER_ROT_SPEED * self.app.delta_time

        key_state = pg.key.get_pressed()

        if key_state[pg.K_LEFT] or key_state[pg.K_q]:
            self.angle += rot_speed
        if key_state[pg.K_RIGHT] or key_state[pg.K_e]:
            self.angle -= rot_speed

        if key_state[pg.K_w]:
            print('w')
            self.inc += vec2(0, -speed)
            self.last_direction_mult[1] = -1
        if key_state[pg.K_s]:
            self.inc += vec2(0, speed)
            self.last_direction_mult[1] = 1
        if key_state[pg.K_a]:
            self.inc += vec2(-speed, 0)
            self.last_direction_mult[0] = -1
            if self.flipped_right:
                self.flipped_right = False
        if key_state[pg.K_d]:
            self.inc += vec2(speed, 0)
            self.last_direction_mult[0] = 1
            if not self.flipped_right:
                self.flipped_right = True
        if self.inc.x or self.inc.y:
            if not self.inc.x:
                self.last_direction_mult[0] = 0
            if not self.inc.y:
                self.last_direction_mult[1] = 0
            if self.inc.x and self.inc.y:
                self.inc *= self.diag_move_corr
                
            if not self.walking:
                self.start_walking()
        else:
            if self.walking:
                self.stop_walking()
        self.inc.rotate_ip_rad(-self.angle)


    def single_fire(self, event):
        if event.key == pg.K_UP or event.key == pg.K_SPACE:
            Bullet(app=self.app)

    def check_collision(self):
        hit = pg.sprite.spritecollide(self, self.app.collision_group,
                                      dokill=False, collided=pg.sprite.collide_mask)
        if not hit:
            if self.inc.x or self.inc.y:
                self.prev_inc = self.inc
        else:
            self.inc = -self.prev_inc
            if hit[0].does_damage:
                self.health -= 1

    def update(self):
        super().update()
        self.control()
        #self.check_collision()
        self.move()

    def move(self):
        self.offset += self.inc
















