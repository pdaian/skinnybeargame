import sys
import pygame as pg
pg.init()

vec2 = pg.math.Vector2

RES = WIDTH, HEIGHT = vec2(1600, 900)
RES = WIDTH, HEIGHT = vec2(1600, 900)
#RES = WIDTH, HEIGHT = vec2(3440, 1440) # just for fun lol

CENTER = H_WIDTH, H_HEIGHT = RES // 2
TILE_SIZE = 200  #

PLAYER_SPEED = 0.4
PLAYER_ROT_SPEED = 0.001

BG_COLOR = 'olivedrab'  #
NUM_ANGLES = 1  # multiple of 360 -> 24, 30, 36, 40, 45, 60, 72, 90, 120, 180
if len(sys.argv) > 1:
	NUM_ANGLES = int(sys.argv[1])
	if len(sys.argv) > 2:
		RES = WIDTH, HEIGHT = vec2(3440, 1440) # fullscreen

OFFSETS = {'blacktop': -1, 'gravel': 5000}
OFFSETS_ENABLED = set(OFFSETS.keys())

# entity settings
ENTITY_SPRITE_ATTRS = {
    'player': {
        'path': 'assets/entities/level1/sb/sb.png',
        'additional_states': { 'walking':  'assets/entities/level1/sb/sbwalk.png'},
        'mask_path': 'assets/entities/player/mask.png',
        'num_layers': 10,
        'scale': 0.4,
        'y_offset': 0,
        'reverse': True,
    },
    'kitty': {
        'path': 'assets/entities/cats/kitty.png',
        'num_layers': 8,
        'scale': 0.8,
        'y_offset': -20,
    },
    'explosion': {
        'num_layers': 10,
        'scale': .5,
        'path': 'assets/entities/level1/redexplosion1.png',
        'y_offset': 50, 
        'reverse': True
    },
    'objectexplosion': {
        'num_layers': 7,
        'scale': 2,
        'path': 'assets/entities/explosion/explosion.png',
        'y_offset': 50, 
        'reverse': True

    },
    'pigeon': {
        'path': 'assets/entities/level1/enemies/pigeon/pigeon.png',
        'num_layers': 3,
        'scale': 10,
        'y_offset': 50,
        'health': 10,
    },
    'entityspawner': {
        'path': 'assets/entities/pixel.png',
        'num_layers': 1,
        'scale': 1,
        'y_offset': 1000,
    },
    'bullet': {
        'num_layers': 1,
        'scale': 0.8,
        'path': 'assets/entities/level1/heart.png',
        'y_offset': 50,
    },
}

# stacked sprites settings
'''mask_layer - index of the layer from which we get the mask for collisions 
and is also cached for all angles of the object, set manually or by default 
equal to num_layer // 2'''

STACKED_SPRITE_ATTRS = {
    'blacktop': {
        'num_layers': 1,
        'scale': 6.2,
        'path': 'assets/entities/level1/town/blacktop.png',
        'y_offset': 50,
        'outline': False,
   },
   'gravel': {
        'num_layers': 1,
        'scale': 6.4,
        'path': 'assets/entities/level1/town/gravel.png',
        'y_offset': 0,
        'outline': False,
   },
   #'wellington': {
   #     'path': 'assets/entities/level1/town/wellington.png',
   #     'num_layers': 35,
   #     'mask_layer': 31,
   #     'scale': 15,
  #      'y_offset': -300,
   #     'reverse': True,
    #    'outline': False,

   # },
    'sphere': {
        'path': 'assets/stacked_sprites/sphere.png',
        'num_layers': 13,
        'scale': 6,
        'y_offset': 0,
        'mask_layer': 4,
    },
    'pancake': {
        'path': 'assets/stacked_sprites/pancake.png',
        'num_layers': 11,
        'scale': 7,
        'y_offset': 0,
        'mask_layer': 4,
    },
    'cup': {
        'path': 'assets/stacked_sprites/cup.png',
        'num_layers': 13,
        'scale': 8,
        'y_offset': 10,
    },
    'crate': {
        'path': 'assets/stacked_sprites/crate.png',
        'num_layers': 16,
        'scale': 5,
        'y_offset': 10,
    },
    'grass': {
        'path': 'assets/stacked_sprites/grass.png',
        'num_layers': 11,
        'scale': 7,
        'y_offset': 50,
        'outline': False,
    },
    'blue_tree': {
        'path': 'assets/stacked_sprites/blue_tree.png',
        'num_layers': 43,
        'scale': 10,
        'y_offset': -20,
        'transparency': True,
        'mask_layer': 3,
    },
    'car': {
        'path': 'assets/stacked_sprites/car.png',
        'num_layers': 9,
        'scale': 10,
        'y_offset': 10,
        'health': 15,

    },
    'van': {
        'path': 'assets/stacked_sprites/van.png',
        'num_layers': 20,
        'scale': 6,
        'y_offset': 10,
        'health': 25,
    },
    'tank': {
        'path': 'assets/stacked_sprites/tank.png',
        'num_layers': 17,
        'scale': 8,
        'y_offset': 0,
        'mask_layer': 4,
        'health': 50,
    },
}
