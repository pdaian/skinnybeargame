from entity import Entity
from settings import TILE_SIZE
from pygame import math as pgm
from threadutils import threaded

@threaded
def run_enemy_loop(enemy_spawners, app):
    import time
    enemies = []
    for enemy_spawner in enemy_spawners:
        enemy_spawner.last_updated = time.time()
        if enemy_spawner.insta:
            # either spawn after one full cycle or instantly depending on settings
            enemy_spawner.last_updated -= enemy_spawner.spawn_every
        enemy_spawner.enemies_spawned = []
    print("spawners", enemy_spawners)
    while not app.done:
        # cleanup any newly dead enemies
        startcleanup = time.time()
        live_enemies = []
        for enemy in enemies:
            if enemy.health > 0:
                live_enemies.append(enemy)
        enemies = live_enemies
        # same cleanup for enemy spawner to prevent too much accumulation
        for enemy_spawner in enemy_spawners:
            live_enemies = []
            for enemy in enemy_spawner.enemies_spawned:
                if enemy.health > 0 and enemy.generation == app.generation:
                    print(enemy.health, enemy.name)
                    live_enemies.append(enemy)
            enemy_spawner.enemies_spawned = live_enemies
        print("cleanup took", startcleanup  - time.time())
        
        # spawn enemies if needed
        for enemy_spawner in enemy_spawners:
            if time.time() - enemy_spawner.last_updated > enemy_spawner.spawn_every:
                print("spawning", enemy_spawner.spawn_name)
                enemy_spawner.last_updated = time.time()
                if len(enemy_spawner.enemies_spawned) > 0:
                    if enemy_spawner.enemies_spawned[-1].health > 0:
                        print("declining to spawn; enemy exists with health")
                        continue # nothing further to do at this spawner
                enemy = Entity(app, name=enemy_spawner.spawn_name, pos=enemy_spawner.pos/TILE_SIZE, collision=True)
                enemy.follow_speed = enemy_spawner.follow_speed
                enemy.follow_within = enemy_spawner.follow_within
                enemy.does_damage = enemy_spawner.does_damage
                enemy.following = False
                enemy.generation = app.generation
                print("spawning done", enemy.pos)
                enemy_spawner.enemies_spawned.append(enemy)
                enemies.append(enemy)
        print("sleeping")
        
        # update all active enemies to follow player
        for enemy in enemies:
            player_pos = pgm.Vector2(app.player.rect.center)
            enemy_pos = pgm.Vector2(enemy.rect.center)
            print("active enemy", enemy_pos, "with player at", player_pos)
            vector_to = player_pos - enemy_pos
            distance_away = vector_to.magnitude()
            print("enemy is", distance_away, "from player on vector", vector_to)
            if distance_away < enemy.follow_within:
                enemy.following = True
            if enemy.following:
                normalized_vector = vector_to
                if distance_away != 0:
                    normalized_vector /= distance_away
                print("setting velocity to", normalized_vector)
                enemy.velocity = normalized_vector

        # enemy attack loop; shoot attacks at player
        
        time.sleep(.5)
        print("enemy loop done")
