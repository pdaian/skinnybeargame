from stacked_sprite import *
from random import uniform
from entity import Entity
import enemies

P = 'player'
K = 'kitty'  # entity
A, B, C, D, E, F, G, H = 'van', 'tank', 'blue_tree', 'car', 'grass', 'crate', 'cup', 'pancake'
S = 'sphere' # transform object

SCENE = [
    [0, E, 0, E, B, 0, E, 0, 0, E, 0, E, 0, E],
    [E, C, C, C, 0, C, C, 0, E, 0, C, C, C, 0],
    [0, C, 0, 0, 0, 0, E, C, 0, C, 0, H, K, C],
    [C, 0, 0, E, C, 0, 0, C, C, 0, 0, 0, 0, C],
    [C, E, 0, 0, P, E, 0, E, 0, 0, F, E, 0, C],
    [C, 0, 0, A, E, D, E, S, 0, F, 0, 0, C, 0],
    [0, C, E, 0, 0, 0, E, 0, E, 0, 0, B, C, E],
    [0, C, C, 0, E, 0, C, C, 0, G, E, C, 0, 0],
    [E, 0, 0, C, C, C, C, 0, C, C, C, 0, E, 0],
]

# this hacky janky and slow as fuck replace it
MAP = open("pinehilldowntown_partial_parsed.csv").read().splitlines()
MAP = [x[:-1].split(",") for x in MAP]
for rowindex in range(len(MAP)):
    for columnindex in range(len(MAP[rowindex])):
        if MAP[rowindex][columnindex] == "-1":
             MAP[rowindex][columnindex] = 0

MAP_SIZE = MAP_WIDTH, MAP_HEIGHT = vec2(len(MAP), len(MAP[0]))
MAP_CENTER = MAP_SIZE / 2
print(MAP)


class Scene:
    def __init__(self, app):
        self.app = app
        self.transform_objects = []
        self.enemy_spawners = []
        self.load_scene()
        enemies.run_enemy_loop(self.enemy_spawners, app)

    def load_scene(self):
        rand_rot = lambda: uniform(0, 360)
        rand_pos = lambda pos: pos + vec2(uniform(-0.25, 0.25))

        for j, row in enumerate(MAP):
            for i, name in enumerate(row):
                pos = vec2(i, j)
                # + vec2(0.5)
                if name == 'player':
                    self.app.player.offset = pos * TILE_SIZE
                elif name == 'kitty':
                    Entity(self.app, name=name, pos=pos, collision=False)
                elif name == 'pigeon':
                    spawner = Entity(self.app, name='entityspawner', pos=pos, collision=False)
                    spawner.spawn_name = 'pigeon'
                    spawner.spawn_every = 15
                    spawner.insta = True
                    spawner.follow_speed = 20.0
                    spawner.follow_within = 500.0
                    spawner.stop_following_at = 300.0
                    spawner.does_damage = True
                    print("spawner pos", pos, spawner.pos)
                    self.enemy_spawners.append(spawner)
                elif name == 'blue_tree':
                    StackedSprite(self.app, name=name, pos=rand_pos(pos), rot=rand_rot())
                elif name == 'grass':
                    StackedSprite(self.app, name=name, pos=rand_pos(pos), rot=rand_rot(),
                                  collision=False)
                elif name == 'sphere':
                    obj = StackedSprite(self.app, name=name, pos=rand_pos(pos), rot=rand_rot())
                    self.transform_objects.append(obj)
                elif name == "blacktop" or name=="gravel":
                    print("placing", name, pos)
                    StackedSprite(self.app, name=name, pos=pos, collision=False)
                elif name == "wellington":
                    StackedSprite(self.app, name=name, pos=pos, rot=90)
                elif name:
                    StackedSprite(self.app, name=name, pos=rand_pos(pos), rot=rand_rot())

    def get_closest_object_to_player(self):
        closest = sorted(self.app.transparent_objects, key=lambda e: e.dist_to_player)
        if len(closest) == 0:
            return # no transparent sprites nothing to do
        closest[0].alpha_trigger = True
        closest[1].alpha_trigger = True

    def transform(self):
        for obj in self.transform_objects:
            obj.rot = 30 * self.app.time

    def update(self):
        self.get_closest_object_to_player()
        self.transform()













