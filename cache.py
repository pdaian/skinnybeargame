from settings import *
from threadutils import threaded
import time
from pygame._sdl2 import Texture, Image
import gpurotate
import numpy
import pygame.pixelcopy
import pickle
import lzma

finished_sprites = set()



# https://github.com/pygame/pygame/issues/1244
def make_surface_rgba(array, amask):
    """Returns a surface made from a [w, h, 4] numpy array with per-pixel alpha
    """
    shape = array.shape
    if len(shape) != 3 and shape[2] != 4:
        raise ValueError("Array not RGBA")

    # Create a surface the same width and height as array and with
    # per-pixel alpha.
    surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:,:,0:3])

    # Copy the alpha part of array to the surface using a pixels-alpha
    # view of the surface.
    surface_alpha = numpy.array(surface.get_view('A'), copy=False)
    print(amask)
    for i in amask:
        for z in i:
            if z != 255:
                print(z)
    surface_alpha[:,:] = amask

    return surface




class Cache:
    def __init__(self):
        self.stacked_sprite_cache = {}
        self.entity_sprite_cache = {}
        self.viewing_angle = 360 // NUM_ANGLES
        self.outline_thickness = 5
        self.alpha_value = 70  #
        self.get_stacked_sprite_cache()
        self.get_entity_sprite_cache()
            

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

        if True: # todo cache exists switch
            with lzma.open('cache/%s' % (obj_name), 'r') as f:
                pickle_data = pickle.load(f)
            unscaled_images = pickle_data[0]
            masks = pickle_data[1]
            alphas = pickle_data[2]
            unscaled_images = [make_surface_rgba(unscaled_images[i], alphas[i]) for i in range(len(unscaled_images))]
            self.stacked_sprite_cache[obj_name]['rotated_sprites'] = [pg.transform.flip(pg.transform.scale(x, vec2(x.get_size()) * attrs['scale']/4.0), False, False) for x in unscaled_images]
            self.stacked_sprite_cache[obj_name]['collision_masks'] = [pg.mask.from_surface(pg.surfarray.make_surface(x)) for x in masks]
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
                    surf = pg.transform.flip(sprite_surf, True, True)
                    masks.append(pg.surfarray.pixels3d(surf))
                    mask = pg.mask.from_surface(surf)
                    self.stacked_sprite_cache[obj_name]['collision_masks'][angle] = mask

            # ~ # get outline TODO do i want to re-enable this or nah
            # ~ if outline:
                # ~ outline_coords = pg.mask.from_surface(sprite_surf).outline()
                # ~ pg.draw.polygon(sprite_surf, 'black', outline_coords, self.outline_thickness)

            # get alpha sprites
            if transparency:  #
                alpha_sprite = sprite_surf.copy()
                alpha_sprite.set_alpha(self.alpha_value)
                alpha_sprite = pg.transform.flip(alpha_sprite, True, True)
                self.stacked_sprite_cache[obj_name]['alpha_sprites'][angle] = alpha_sprite

            image = pg.transform.flip(sprite_surf, True, True)
            all_angles.append(pg.surfarray.pixels3d(image))
            surface_alpha = numpy.array(image.get_view('A'), copy=False)
            alphas.append(surface_alpha)
            image = pg.transform.scale(image, vec2(image.get_size()) * attrs['scale']/4.0)

            self.stacked_sprite_cache[obj_name]['rotated_sprites'][angle] = image
        with lzma.open('cache/%s' % (obj_name), 'wb') as f:
            pickle.dump([all_angles, masks, alphas], f)
        finished_sprites.add(obj_name)


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
