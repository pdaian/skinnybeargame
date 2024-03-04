from settings import *
from threadutils import threaded
import time, os
from pygame._sdl2 import Texture, Image
import gpurotate
import numpy
import pygame.pixelcopy
import pickle
import lzma, cv2

finished_sprites = set()

def make_surface_rgba(image):
    surface = pygame.image.frombuffer(image[0], (image[1], image[2]), 'RGBA').convert_alpha()
    return surface

class Cache:
    def __init__(self):
        load = time.time()
        self.stacked_sprite_cache = {}
        self.entity_sprite_cache = {}
        self.viewing_angle = 360 // NUM_ANGLES
        self.outline_thickness = 5
        self.alpha_value = 70  #
        self.get_stacked_sprite_cache()
        self.get_entity_sprite_cache()
        print("loaded cache in", time.time() - load)

    def get_entity_sprite_cache(self):
        for sprite_name in ENTITY_SPRITE_ATTRS:
            self.entity_sprite_cache[sprite_name] = {
                'images': None
            }
            attrs = ENTITY_SPRITE_ATTRS[sprite_name]
            images = self.get_layer_array(attrs)
            self.entity_sprite_cache[sprite_name]['all_states'] = {'default': images}

            if 'additional_states' in attrs:
                for state in attrs['additional_states']:
                    keyword = lambda x : x['additional_states'][state]
                    state_layer = self.get_layer_array(attrs, keyword=keyword)
                    self.entity_sprite_cache[sprite_name]['all_states'][state] = state_layer

            mask = self.get_entity_mask(attrs, images)
            self.entity_sprite_cache[sprite_name]['mask'] = mask
            
            self.entity_sprite_cache[sprite_name]['health'] = attrs['health'] if 'health' in attrs else None


    def get_entity_mask(self, attrs, images):
        path = attrs.get('mask_path', False)
        if not path:
            return pg.mask.from_surface(images[0])
        else:
            scale = attrs['scale']
            mask_image = pg.image.load(path).convert_alpha()
            mask_image = pg.transform.scale(mask_image, vec2(mask_image.get_size()) * scale)
            return pg.mask.from_surface(mask_image)

    def get_stacked_sprite_cache(self):
        for obj_name in STACKED_SPRITE_ATTRS:
            self.stacked_sprite_cache[obj_name] = {
                'rotated_sprites': {},
                'alpha_sprites': {},
                'collision_masks': {},
                'health': STACKED_SPRITE_ATTRS[obj_name]['health'] if 'health' in STACKED_SPRITE_ATTRS[obj_name] else None
            }
            attrs = STACKED_SPRITE_ATTRS[obj_name]
            self.run_prerender(obj_name, attrs)
        while not len(STACKED_SPRITE_ATTRS) == len(finished_sprites):
            time.sleep(1)

    def get_all_rotated_slices(self, attrs, num_slices, viewing_angle, scale):
        return gpurotate.get_all_slices(attrs, num_slices, NUM_ANGLES, viewing_angle, scale)

    @threaded
    def run_prerender(self, obj_name, attrs):
        global finished_sprites

        if os.path.exists('cache/%s' % (obj_name)):
            # todo cache fail to load logic
            print("started", obj_name)
            with lzma.open('cache/%s' % (obj_name), 'r') as f:
                pickle_data = pickle.load(f)
            unscaled_images = pickle_data[0]
            masks = pickle_data[1]
            unscaled_images = [make_surface_rgba(unscaled_images[i]) for i in range(len(unscaled_images))]
            self.stacked_sprite_cache[obj_name]['rotated_sprites'] = [pg.transform.scale(x, vec2(x.get_size()) * attrs['scale']/4.0).convert_alpha() for x in unscaled_images]
            masks = [make_surface_rgba(x) for x in masks]            
            self.stacked_sprite_cache[obj_name]['collision_masks'] = [pg.mask.from_surface(pg.transform.scale(x, vec2(x.get_size()) * attrs['scale']/4.0)) for x in masks]
            finished_sprites.add(obj_name)
            print("done w", obj_name)
            return
        layer_array = self.get_layer_array(attrs, ignore_scale=True)

        all_angles = []
        masks = []
        alphas = []
        outline = attrs.get('outline', True)
        transparency = attrs.get('transparency', False)
        mask_layer = attrs.get('mask_layer', attrs['num_layers'] // 2)

        for angle in range(NUM_ANGLES):
            print("rendering", angle, obj_name)
            surf = pg.Surface(layer_array[0].get_size())
            surf = pg.transform.rotate(surf, angle * self.viewing_angle)
            sprite_surf = pg.Surface([surf.get_width(), surf.get_height()
                                      + 4 * attrs['num_layers']],  flags=pygame.SRCALPHA)
            sprite_surf.fill('khaki')
            sprite_surf.set_colorkey('khaki')

            for ind, layer in enumerate(layer_array):
                layer = pg.transform.rotate(layer, angle * self.viewing_angle)
                sprite_surf.blit(layer, (0, 4 * ind))

                # get collision mask
                if ind == mask_layer:
                    surf = pg.transform.flip(sprite_surf, True, True).convert_alpha()
                    masks.append([pg.image.tostring(surf, 'RGBA'), surf.get_width(), surf.get_height()])
                    surf = pg.transform.scale(surf, vec2(surf.get_size()) * attrs['scale']/4.0)
                    mask = pg.mask.from_surface(surf)
                    self.stacked_sprite_cache[obj_name]['collision_masks'][angle] = mask

            # get outline
            if outline:
                outline_coords = pg.mask.from_surface(sprite_surf).outline()
                pg.draw.polygon(sprite_surf, 'black', outline_coords, int(self.outline_thickness / (attrs['scale']/4.0)))

            # get alpha sprites
            if transparency:  #
                alpha_sprite = sprite_surf.copy()
                alpha_sprite.set_alpha(self.alpha_value)
                alpha_sprite = pg.transform.flip(alpha_sprite, True, True)
                self.stacked_sprite_cache[obj_name]['alpha_sprites'][angle] = alpha_sprite

            image = pg.transform.flip(sprite_surf, True, True).convert_alpha()
            all_angles.append([pg.image.tostring(image, 'RGBA'), image.get_width(), image.get_height()])

            image = pg.transform.scale(image, vec2(image.get_size()) * attrs['scale']/4.0)
            self.stacked_sprite_cache[obj_name]['rotated_sprites'][angle] = image

        with lzma.open('cache/%s' % (obj_name), 'wb') as f:
            pickle.dump([all_angles, masks], f)
        finished_sprites.add(obj_name) # this is unsafe replace w progress


    def get_layer_array(self, attrs, keyword=lambda x : x['path'], ignore_scale=False):
        # load sprite sheet
        sprite_sheet = pg.image.load(keyword(attrs)).convert_alpha()
        # scaling
        scale = 4 if ignore_scale else attrs['scale']
        sprite_sheet = pg.transform.scale(sprite_sheet,
                                          vec2(sprite_sheet.get_size()) * scale)
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()
        sprite_height = sheet_height // attrs['num_layers']
        # new height to prevent error
        sheet_height = sprite_height * attrs['num_layers']
        # get sprites
        layer_array = []
        for y in range(0, sheet_height, sprite_height):
            sprite = sprite_sheet.subsurface((0, y, sheet_width, sprite_height))
            layer_array.append(sprite)
        if 'reverse' in attrs and attrs['reverse']:
            returnval = layer_array
        else:
            returnval = layer_array[::-1]
        return returnval
