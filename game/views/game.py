import arcade
import random
import math
import os
from data import Bullet, Enemy, PlayerSkin, Weapon
from typing import List

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "2D Shooter Arena"

ENEMY_SPEED = 2
BULLET_SPEED = 10
ENEMY_SPAWN_RATE = 60


class GameView(arcade.View):
    def __init__(self, main_menu_view, user_id = 1):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.user_id = user_id
        self.db = main_menu_view.database
        self.user_data = self.db.get_user_data(user_id) or {}
        self.user_stats = self.db.get_user_stats_summary(user_id) or {}
        skin_name = self.user_data.get('current_skin', 'Солдат')
        skin_level = self.user_data.get('skin_level', 1)
        if skin_name == "Солдат":
            self.player_skin = PlayerSkin(name="Солдат", max_health=100, speed=3.0)
        elif skin_name == "Бандит":
            self.player_skin = PlayerSkin(name="Бандит", max_health=80, speed=5.0)
        else:
            self.player_skin = PlayerSkin(name="Джангист", max_health=150, speed=6.0)

        self.player_skin.level = skin_level
        
        weapon_name = self.user_data.get('current_weapon', 'Пистолет')
        weapon_level = self.user_data.get('weapon_level', 1)

        if weapon_name == "Пистолет":
            print("\nAAAAAA\n")
            self.weapon = Weapon(name="Пистолет", damage=10, fire_rate=0.5)
        elif weapon_name == "Дробовик":
            self.weapon = Weapon(name="Дробовик", damage=30, fire_rate=1.2)
        elif weapon_name == "Автомат":
            self.weapon = Weapon(name="Автомат", damage=15, fire_rate=0.2)
        elif weapon_name == "Снайперка":
            self.weapon = Weapon(name="Снайперка", damage=50, fire_rate=1.5)
        else:
            self.weapon = Weapon(name="Пистолет", damage=10, fire_rate=0.5)

        self.weapon.level = weapon_level

        self.tile_map = None
        self.scene = None
        self.wall_list = None
        self.spawn_list = None
        self.decoration_list = None
        self.background_list = None
        self.physics_engine = None

        # Параметры игрока (основанные на скине)
        self.player_health = self.player_skin.max_health
        self.player_max_health = self.player_skin.max_health
        self.player_speed = self.player_skin.speed
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_radius = 25
        
        self.player_sprite = None
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.enemy_spawn_timer = 0
        self.score = 0
        self.total_kills = 0
        self.game_time = 0
        self.game_over = False
        self.keys_pressed = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.shoot_cooldown = 0
        
        self.load_sounds()
        self.load_tmx_map()
        self.setup_player()
    
    def load_tmx_map(self):
        try:
            map_path = "assets/tilemaps/lv1.tmx"

            if not os.path.exists(map_path):
                print(f"Файл карты не найден: {map_path}")
                print("Создаю карту по умолчанию...")
                self.create_default_map()
                return

            layer_options = {
                "walls": {
                    "use_spatial_hash": True,
                },
                "spawn": {
                    "use_spatial_hash": False,
                },
                "decorations": {
                    "use_spatial_hash": False,
                },
                "background": {
                    "use_spatial_hash": False,
                }
            }

            self.tile_map = arcade.load_tilemap(
                map_path, 
                scaling=1.0,
                layer_options=layer_options
            )

            self.scene = arcade.Scene.from_tilemap(self.tile_map)
            self.wall_list = self.scene.get_sprite_list("walls")
            self.spawn_list = self.scene.get_sprite_list("spawn")
            self.decoration_list = self.scene.get_sprite_list("decorations")
            self.background_list = self.scene.get_sprite_list("background")
            if self.background_list is None:
                self.background_list = arcade.SpriteList()
            
            print(f"TMX карта загружена успешно!")
            print(f"Размер: {self.tile_map.width}x{self.tile_map.height} тайлов")
            print(f"Спрайтов стен: {len(self.wall_list) if self.wall_list else 0}")
            print(f"Точек спавна: {len(self.spawn_list) if self.spawn_list else 0}")
            
        except Exception as e:
            print(f"Ошибка загрузки TMX карты: {e}")
            print("Создаю карту по умолчанию...")
            self.create_default_map()
    
    def create_default_map(self):
        print("Создание карты по умолчанию...")
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.spawn_list = arcade.SpriteList()
        self.decoration_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        tile_size = 64
        map_width = SCREEN_WIDTH // tile_size
        map_height = SCREEN_HEIGHT // tile_size
        for x in range(map_width):
            self.create_wall_sprite(x * tile_size + tile_size//2, tile_size//2, tile_size)
            self.create_wall_sprite(x * tile_size + tile_size//2, SCREEN_HEIGHT - tile_size//2, tile_size)
        
        for y in range(map_height):
            self.create_wall_sprite(tile_size//2, y * tile_size + tile_size//2, tile_size)
            self.create_wall_sprite(SCREEN_WIDTH - tile_size//2, y * tile_size + tile_size//2, tile_size)

        for _ in range(10):
            x = random.randint(2, map_width - 3) * tile_size + tile_size//2
            y = random.randint(2, map_height - 3) * tile_size + tile_size//2
            self.create_wall_sprite(x, y, tile_size)

        for i in range(5):
            self.create_spawn_sprite(random.randint(100, SCREEN_WIDTH-100), SCREEN_HEIGHT-100)
            self.create_spawn_sprite(random.randint(100, SCREEN_WIDTH-100), 100)
            self.create_spawn_sprite(100, random.randint(100, SCREEN_HEIGHT-100))
            self.create_spawn_sprite(SCREEN_WIDTH-100, random.randint(100, SCREEN_HEIGHT-100))

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("walls", sprite_list=self.wall_list)
        self.scene.add_sprite_list("spawn", sprite_list=self.spawn_list)
        self.scene.add_sprite_list("decorations", sprite_list=self.decoration_list)
        self.scene.add_sprite_list("background", sprite_list=self.background_list)
    
    def create_wall_sprite(self, x, y, size):
        sprite = arcade.SpriteSolidColor(size, size, arcade.color.BROWN)
        sprite.center_x = x
        sprite.center_y = y
        self.wall_list.append(sprite)
    
    def create_spawn_sprite(self, x, y):
        sprite = arcade.SpriteSolidColor(10, 10, arcade.color.TRANSPARENT_BLACK)
        sprite.center_x = x
        sprite.center_y = y
        self.spawn_list.append(sprite)
    
    def setup_player(self):
        self.player_sprite = arcade.SpriteSolidColor(
            self.player_radius * 2, 
            self.player_radius * 2, 
            arcade.color.BLUE
        )
        self.player_sprite.center_x = self.player_x
        self.player_sprite.center_y = self.player_y
        if self.wall_list:
            self.physics_engine = arcade.PhysicsEngineSimple(
                self.player_sprite, 
                self.wall_list
            )
    
    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)
        print(f"Игра начата!")
        print(f"Скин: {self.player_skin.name} (Уровень {self.player_skin.level})")
        print(f"Оружие: {self.weapon.name} (Уровень {self.weapon.level})")
        print(f"Здоровье: {self.player_health}/{self.player_max_health}")
        print(f"Скорость: {self.player_speed}")
        print(f"Урон оружия: {self.weapon.damage}")
    
    def on_draw(self):
        self.clear()
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            arcade.color.DARK_GRAY
        )

        self.background_list.draw()
        self.decoration_list.draw()
        for enemy in self.enemies:
            enemy.draw()
        for bullet in self.bullets:
            bullet.draw()
        self.wall_list.draw()
        self.draw_player()
        self.draw_ui()
        if self.game_over:
            self.draw_game_over()
    
    def draw_player(self):
        if self.player_skin.name == "Солдат":
            body_color = arcade.color.ARMY_GREEN
        elif self.player_skin.name == "Бандит":
            body_color = arcade.color.DARK_RED
        else:
            body_color = arcade.color.DARK_BLUE

        arcade.draw_circle_filled(
            self.player_x, self.player_y,
            self.player_radius, body_color
        )
        arcade.draw_circle_outline(
            self.player_x, self.player_y,
            self.player_radius, arcade.color.BLACK, 3
        )
        dx = self.mouse_x - self.player_x
        dy = self.mouse_y - self.player_y
        angle = math.atan2(dy, dx)
        eye_x = self.player_x + math.cos(angle) * 15
        eye_y = self.player_y + math.sin(angle) * 15
        arcade.draw_circle_filled(eye_x, eye_y, 8, arcade.color.WHITE)
        arcade.draw_circle_filled(eye_x, eye_y, 4, arcade.color.BLACK)
        weapon_length = 30
        weapon_end_x = self.player_x + math.cos(angle) * weapon_length
        weapon_end_y = self.player_y + math.sin(angle) * weapon_length
        
        arcade.draw_line(
            self.player_x, self.player_y,
            weapon_end_x, weapon_end_y,
            arcade.color.BLACK, 4
        )
        health_width = 60
        health_ratio = self.player_health / self.player_max_health
        arcade.draw_lbwh_rectangle_filled(
            self.player_x - health_width/2, 
            self.player_y + self.player_radius + 25,
            health_width, 8, 
            arcade.color.DARK_GRAY
        )
        arcade.draw_lbwh_rectangle_filled(
            self.player_x - health_width/2,
            self.player_y + self.player_radius + 25,
            health_width * health_ratio, 6,
            arcade.color.GREEN if health_ratio > 0.3 else arcade.color.RED
        )
    
    def draw_ui(self):
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, 80,
            arcade.color.DARK_SLATE_GRAY
        )
        arcade.draw_text(
            f"👤 {self.user_data.get('username', 'Игрок')}",
            20, SCREEN_HEIGHT - 40,
            arcade.color.WHITE, 22,
            font_name="arial", bold=True
        )
        
        arcade.draw_text(
            f"Уровень {self.player_skin.level}",
            20, SCREEN_HEIGHT - 40,
            arcade.color.RED, 18,
            font_name="arial"
        )

        stats = [
            f"{self.player_health}/{self.player_max_health}",
            f"Счёт: {self.score}",
            f"Время: {int(self.game_time)}с",
            f"Убито: {self.total_kills}",
            f"{self.weapon.name}"
        ]
        
        for i, stat in enumerate(stats):
            arcade.draw_text(
                stat,
                SCREEN_WIDTH // 2 - 300 + i * 150, 
                SCREEN_HEIGHT - 40,
                arcade.color.RED, 20,
                font_name="arial"
            )

        # Для одарённых
        arcade.draw_text(
            "WASD - движение | ЛКМ - стрельба | ESC - выход",
            SCREEN_WIDTH // 2, 30,
            arcade.color.LIGHT_GRAY, 18,
            anchor_x="center", font_name="arial"
        )
    
    def load_sounds(self):
        try:
            shot_sound_path = "../assets/sounds/shot.mp3"
            if os.path.exists(shot_sound_path):
                self.shot_sound = arcade.load_sound(shot_sound_path)
                print(f"Звук выстрела загружен: {shot_sound_path}")
            else:
                print(f"Файл звука выстрела не найден: {shot_sound_path}")
                self.shot_sound = None

        except Exception as e:
            print(f"Ошибка загрузки звуков: {e}")
            self.sounds_loaded = False
    
    def play_sound(self, sound, volume=1.0, pan=0.0):
        try:
            sound.play(volume=volume, pan=pan)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
    
    def play_shot_sound(self):
        if self.shot_sound:
            if self.weapon.name == "Пистолет":
                volume = 0.7
            elif self.weapon.name == "Дробовик":
                volume = 1.0
            elif self.weapon.name == "Автомат":
                volume = 0.6
            else:
                volume = 0.8
            self.play_sound(self.shot_sound, volume=volume)

    def draw_game_over(self):
        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT // 2 - 150,
            640, 300,
            arcade.color.DARK_SLATE_GRAY
        )
        
        arcade.draw_lbwh_rectangle_outline(
            SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT // 2 - 150,
            640, 300,
            arcade.color.GOLD, 4
        )
        
        arcade.draw_text(
            "Game Over((",  # простите, шрифта не нашлось
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90,
            arcade.color.RED, 48,
            anchor_x="center", bold=True
        )
        
        arcade.draw_text(
            f"Ваш счёт: {self.score}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
            arcade.color.WHITE, 32,
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"Убито врагов: {self.total_kills}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
            arcade.color.WHITE, 24,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Нажмите ESC для выхода в меню",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
            arcade.color.YELLOW, 20,
            anchor_x="center"
        )
    
    def on_update(self, delta_time):
        if self.game_over:
            return
        
        self.game_time += delta_time
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.handle_player_movement()
        if self.physics_engine:
            self.physics_engine.update()
            self.player_x = self.player_sprite.center_x
            self.player_y = self.player_sprite.center_y
        self.update_bullets()
        self.update_enemies()
        self.spawn_enemies()
        self.check_collisions()
        if self.player_health <= 0:
            self.end_game()
    
    def handle_player_movement(self):
        dx, dy = 0, 0
        if arcade.key.W in self.keys_pressed:
            dy += self.player_speed
        if arcade.key.S in self.keys_pressed:
            dy -= self.player_speed
        if arcade.key.A in self.keys_pressed:
            dx -= self.player_speed
        if arcade.key.D in self.keys_pressed:
            dx += self.player_speed

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        if self.player_sprite:
            self.player_sprite.change_x = dx
            self.player_sprite.change_y = dy
        if not self.physics_engine:
            self.player_x += dx
            self.player_y += dy
            self.player_x = max(self.player_radius, min(SCREEN_WIDTH - self.player_radius, self.player_x))
            self.player_y = max(self.player_radius, min(SCREEN_HEIGHT - self.player_radius, self.player_y))
    
    def update_bullets(self):
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            bullet.update()
            if (bullet.x < 0 or bullet.x > SCREEN_WIDTH or 
                bullet.y < 0 or bullet.y > SCREEN_HEIGHT):
                bullets_to_remove.append(i)
            if self.wall_list:
                for wall in self.wall_list:
                    distance = math.sqrt(
                        (bullet.x - wall.center_x)**2 + 
                        (bullet.y - wall.center_y)**2
                    )
                    if distance < bullet.radius + wall.width / 2:
                        bullets_to_remove.append(i)
                        break
        for i in reversed(bullets_to_remove):
            if i < len(self.bullets):
                self.bullets.pop(i)
    
    def update_enemies(self):
        for enemy in self.enemies:
            enemy.update(self.player_x, self.player_y)
            if self.wall_list:
                for wall in self.wall_list:
                    distance = math.sqrt(
                        (enemy.x - wall.center_x)**2 + 
                        (enemy.y - wall.center_y)**2
                    )
                    if distance < enemy.radius + wall.width / 2:
                        dx = enemy.x - wall.center_x
                        dy = enemy.y - wall.center_y
                        dist = max(0.1, distance)
                        enemy.x += (dx / dist) * 5
                        enemy.y += (dy / dist) * 5
    
    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= ENEMY_SPAWN_RATE and self.spawn_list:
            self.enemy_spawn_timer = 0
            spawn_point = random.choice(self.spawn_list)
            enemy = Enemy(
                x=spawn_point.center_x,
                y=spawn_point.center_y,
                health=30 + int(self.game_time) // 10,
                max_health=30 + int(self.game_time) // 10,
                speed=ENEMY_SPEED + random.uniform(-0.5, 0.5),
                radius=20 + random.randint(-5, 5)
            )
            
            self.enemies.append(enemy)
    
    def check_collisions(self):
        bullets_to_remove = []
        enemies_to_remove = []
        for i, bullet in enumerate(self.bullets):
            for j, enemy in enumerate(self.enemies):
                distance = math.sqrt(
                    (bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2
                )
                
                if distance < bullet.radius + enemy.radius:
                    enemy.health -= self.weapon.damage
                    bullets_to_remove.append(i)
                    
                    if enemy.health <= 0:
                        enemies_to_remove.append(j)
                        self.score += 10
                        self.total_kills += 1
                    break

        for i in reversed(enemies_to_remove):
            self.enemies.pop(i)
        
        for i in reversed(bullets_to_remove):
            if i < len(self.bullets):
                self.bullets.pop(i)

        for enemy in self.enemies:
            distance = math.sqrt(
                (self.player_x - enemy.x)**2 + (self.player_y - enemy.y)**2
            )
            
            if distance < self.player_radius + enemy.radius:
                self.player_health -= 5
                dx = enemy.x - self.player_x
                dy = enemy.y - self.player_y
                dist = max(0.1, distance)
                enemy.x += (dx / dist) * 20
                enemy.y += (dy / dist) * 20
    
    def shoot(self):
        if self.shoot_cooldown > 0:
            return

        self.shoot_cooldown = int(self.weapon.fire_rate * 60)
        dx = self.mouse_x - self.player_x
        dy = self.mouse_y - self.player_y
        dist = max(0.1, math.sqrt(dx*dx + dy*dy))
        bullet = Bullet(
            x=self.player_x,
            y=self.player_y,
            dx=(dx / dist) * BULLET_SPEED,
            dy=(dy / dist) * BULLET_SPEED,
            damage=self.weapon.damage
        )
        self.play_shot_sound()
        self.bullets.append(bullet)
    
    def end_game(self):
        self.game_over = True
        money_earned = self.score // 10
        money_earned = max(10, money_earned)
        current_money = self.user_stats.get('money', 1000)
        new_money = current_money + money_earned
        self.db.update_user_settings(
            self.user_id,
            money=new_money
        )
        self.db.cursor.execute('''
            INSERT INTO game_records (user_id, score, kills, play_time)
            VALUES (?, ?, ?, ?)
        ''', (self.user_id, self.score, self.total_kills, int(self.game_time)))
        self.db.conn.commit()
        
        print(f"Игра завершена!")
        print(f"Счёт: {self.score}")
        print(f"Убито врагов: {self.total_kills}")
        print(f"Заработано денег: {money_earned}")
        print(f"Общее время: {int(self.game_time)} секунд")
    
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        
        if key == arcade.key.ESCAPE:
            if self.game_over:
                self.window.show_view(self.main_menu_view)
            else:
                print("Нажмите ESC еще раз для выхода в меню")

        if key == arcade.key.SPACE:
            self.spawn_enemies()
        if key == arcade.key.P:
            self.score += 100
        if key == arcade.key.H:
            self.player_health = min(self.player_max_health, self.player_health + 50)
        if key == arcade.key.G:
            self.end_game()
    
    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and not self.game_over:
            self.shoot()
