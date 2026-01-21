import arcade
import random
import math
import os
from data import Bullet, Enemy
from typing import List

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "2D Shooter Arena"

PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 10
ENEMY_SPAWN_RATE = 60


class GameView(arcade.View):
    def __init__(self, database):
        super().__init__()
        self.database = database

        self.tile_map = None
        self.scene = None
        self.wall_list = None
        self.spawn_list = None
        self.decoration_list = None
        self.background_list = None
        self.physics_engine = None

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_radius = 25
        self.player_sprite = None
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.enemy_spawn_timer = 0
        self.score = 0
        self.game_time = 0
        self.game_over = False
        self.keys_pressed = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.shoot_cooldown = 0
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
    
    def setup_ui(self):
        pass
    
    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)
        print("Игра начата!")
    
    def on_draw(self):
        self.clear()
        
        # Рисуем фон
        arcade.draw_lbwh_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT, 0,
            arcade.color.DARK_GRAY
        )
        
        # Рисуем фон карты
        self.background_list.draw()
        
        # Рисуем декорации
        self.decoration_list.draw()
        
        # Рисуем врагов
        for enemy in self.enemies:
            enemy.draw()
        
        # Рисуем пули
        for bullet in self.bullets:
            bullet.draw()
        
        # Рисуем стены
        self.wall_list.draw()
        
        # Рисуем игрока (пока как круг)
        self.draw_player()
        
        # Рисуем интерфейс
        self.draw_ui()
        
        # Если игра окончена
        if self.game_over:
            self.draw_game_over()
    
    def draw_player(self):
        """Отрисовка игрока"""
        body_color = arcade.color.GOLD
        
        # Тело
        arcade.draw_circle_filled(
            self.player_x, self.player_y,
            self.player_radius, body_color
        )
        arcade.draw_circle_outline(
            self.player_x, self.player_y,
            self.player_radius, arcade.color.BLACK, 3
        )
        
        # Направление взгляда (к курсору)
        dx = self.mouse_x - self.player_x
        dy = self.mouse_y - self.player_y
        angle = math.atan2(dy, dx)
        
        # Глаза
        eye_x = self.player_x + math.cos(angle) * 15
        eye_y = self.player_y + math.sin(angle) * 15
        arcade.draw_circle_filled(eye_x, eye_y, 8, arcade.color.WHITE)
        arcade.draw_circle_filled(eye_x, eye_y, 4, arcade.color.BLACK)
        
        # Оружие
        weapon_length = 30
        weapon_end_x = self.player_x + math.cos(angle) * weapon_length
        weapon_end_y = self.player_y + math.sin(angle) * weapon_length
        
        arcade.draw_line(
            self.player_x, self.player_y,
            weapon_end_x, weapon_end_y,
            arcade.color.BLACK, 4
        )

        health_width = 60
        health_ratio = 1.0
        arcade.draw_lbwh_rectangle_filled(
            self.player_x, self.player_y + self.player_radius + 25,
            health_width, 8, arcade.color.DARK_GRAY
        )
        arcade.draw_lbwh_rectangle_filled(
            self.player_x - (health_width/2) + (health_width * health_ratio / 2),
            self.player_y + self.player_radius + 25,
            health_width * health_ratio, 6,
            arcade.color.GREEN
        )
    
    def draw_ui(self):
        arcade.draw_lbwh_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_HEIGHT - 60,
            arcade.color.DARK_SLATE_GRAY
        )
        
        stats = [
            f"100/100",
            f"Счёт: {self.score}",
            f"Время: {int(self.game_time)}с",
            f"Врагов: {len(self.enemies)}"
        ]
        
        for i, stat in enumerate(stats):
            arcade.draw_text(
                stat,
                20 + i * 300, SCREEN_HEIGHT - 35,
                arcade.color.RED,
                20,
                font_name="arial"
            )

        arcade.draw_text(
            "WASD - движение | ЛКМ - стрельба | ESC - выход",
            SCREEN_WIDTH // 2, 30,
            arcade.color.LIGHT_GRAY, 18,
            anchor_x="center"
        )
    
    def draw_game_over(self):
        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (0, 0, 0, 180)
        )
        
        arcade.draw_text(
            "ИГРА ОКОНЧЕНА",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
            arcade.color.RED, 64,
            anchor_x="center", bold=True
        )
        
        arcade.draw_text(
            f"Ваш счёт: {self.score}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            arcade.color.WHITE, 36,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Нажмите ESC для выхода в меню",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
            arcade.color.YELLOW, 24,
            anchor_x="center"
        )
    
    def on_update(self, delta_time):
        if self.game_over:
            return
        
        self.game_time += delta_time
        
        # КД стрельбы
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Движение игрока
        self.handle_player_movement()
        
        # Обновление физики (коллизии со стенами)
        if self.physics_engine:
            self.physics_engine.update()
            # Обновляем позицию из спрайта
            self.player_x = self.player_sprite.center_x
            self.player_y = self.player_sprite.center_y
        
        # Обновление пуль
        self.update_bullets()
        
        # Обновление врагов
        self.update_enemies()
        
        # Спавн врагов
        self.spawn_enemies()
        
        # Проверка столкновений
        self.check_collisions()
    
    def handle_player_movement(self):
        dx, dy = 0, 0
        
        if arcade.key.W in self.keys_pressed:
            dy += PLAYER_SPEED
        if arcade.key.S in self.keys_pressed:
            dy -= PLAYER_SPEED
        if arcade.key.A in self.keys_pressed:
            dx -= PLAYER_SPEED
        if arcade.key.D in self.keys_pressed:
            dx += PLAYER_SPEED

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        # Обновляем скорость спрайта игрока
        if self.player_sprite:
            self.player_sprite.change_x = dx
            self.player_sprite.change_y = dy
        
        # Обновляем позицию (если нет физического движка)
        if not self.physics_engine:
            self.player_x += dx
            self.player_y += dy
            
            # Ограничение в пределах экрана
            self.player_x = max(self.player_radius, min(SCREEN_WIDTH - self.player_radius, self.player_x))
            self.player_y = max(self.player_radius, min(SCREEN_HEIGHT - self.player_radius, self.player_y))
    
    def update_bullets(self):
        """Обновление пуль"""
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            bullet.update()
            
            # Удаляем пули за пределами экрана
            if (bullet.x < 0 or bullet.x > SCREEN_WIDTH or 
                bullet.y < 0 or bullet.y > SCREEN_HEIGHT):
                bullets_to_remove.append(i)
            
            # Проверка коллизий пуль со стенами
            if self.wall_list:
                for wall in self.wall_list:
                    distance = math.sqrt(
                        (bullet.x - wall.center_x)**2 + 
                        (bullet.y - wall.center_y)**2
                    )
                    if distance < bullet.radius + wall.width / 2:
                        bullets_to_remove.append(i)
                        break
        
        # Удаляем отмеченные пули
        for i in reversed(bullets_to_remove):
            if i < len(self.bullets):
                self.bullets.pop(i)
    
    def update_enemies(self):
        """Обновление врагов"""
        for enemy in self.enemies:
            enemy.update(self.player_x, self.player_y)
            
            # Проверка коллизий врагов со стенами
            if self.wall_list:
                for wall in self.wall_list:
                    distance = math.sqrt(
                        (enemy.x - wall.center_x)**2 + 
                        (enemy.y - wall.center_y)**2
                    )
                    if distance < enemy.radius + wall.width / 2:
                        # Отталкивание от стены
                        dx = enemy.x - wall.center_x
                        dy = enemy.y - wall.center_y
                        dist = max(0.1, distance)
                        enemy.x += (dx / dist) * 5
                        enemy.y += (dy / dist) * 5
    
    def spawn_enemies(self):
        """Спавн новых врагов из точек спавна"""
        self.enemy_spawn_timer += 1
        
        if self.enemy_spawn_timer >= ENEMY_SPAWN_RATE and self.spawn_list:
            self.enemy_spawn_timer = 0
            
            # Выбираем случайную точку спавна
            spawn_point = random.choice(self.spawn_list)
            
            # Создаем врага
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
        """Проверка столкновений"""
        bullets_to_remove = []
        enemies_to_remove = []
        
        # Пули с врагами
        for i, bullet in enumerate(self.bullets):
            for j, enemy in enumerate(self.enemies):
                distance = math.sqrt(
                    (bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2
                )
                
                if distance < bullet.radius + enemy.radius:
                    # Попадание!
                    enemy.health -= 10  # Заглушка урона
                    bullets_to_remove.append(i)
                    
                    if enemy.health <= 0:
                        enemies_to_remove.append(j)
                        self.score += 10
                    
                    break
        
        # Удаляем пораженных врагов и использованные пули
        for i in reversed(enemies_to_remove):
            self.enemies.pop(i)
        
        for i in reversed(bullets_to_remove):
            if i < len(self.bullets):
                self.bullets.pop(i)
        
        # Враги с игроком
        for enemy in self.enemies:
            distance = math.sqrt(
                (self.player_x - enemy.x)**2 + (self.player_y - enemy.y)**2
            )
            
            if distance < self.player_radius + enemy.radius:
                # Урон игроку
                # self.player_health -= 1  # Раскомментировать когда будет здоровье
                
                # Отталкивание врага
                dx = enemy.x - self.player_x
                dy = enemy.y - self.player_y
                dist = max(0.1, distance)
                enemy.x += (dx / dist) * 20
                enemy.y += (dy / dist) * 20
    
    def shoot(self):
        """Выстрел"""
        if self.shoot_cooldown > 0:
            return
        
        # КД стрельбы
        self.shoot_cooldown = 10  # Заглушка
        
        # Направление к курсору
        dx = self.mouse_x - self.player_x
        dy = self.mouse_y - self.player_y
        dist = max(0.1, math.sqrt(dx*dx + dy*dy))
        
        # Создаем пулю
        bullet = Bullet(
            x=self.player_x,
            y=self.player_y,
            dx=(dx / dist) * BULLET_SPEED,
            dy=(dy / dist) * BULLET_SPEED,
            damage=10  # Заглушка урона
        )
        
        self.bullets.append(bullet)
    
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        
        # if key == arcade.key.ESCAPE:
        #     # Возвращаемся в меню
        #     from main_menu_view import MainMenuView
        #     menu_view = MainMenuView(self.database)
        #     self.window.show_view(menu_view)
        
        # Тестовые клавиши
        if key == arcade.key.SPACE:
            self.spawn_enemies()
        if key == arcade.key.P:
            self.score += 100
    
    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and not self.game_over:
            self.shoot()
