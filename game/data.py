import math
import arcade
from dataclasses import dataclass
from typing import List


@dataclass
class Weapon:
    name: str
    damage: int
    fire_rate: float
    level: int = 1
    upgrade_cost: int = 100

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.5)
        self.fire_rate = max(0.1, self.fire_rate * 0.9)
        self.upgrade_cost = int(self.upgrade_cost * 2)
        return self.upgrade_cost

    @property
    def dps(self):
        return self.damage / self.fire_rate


@dataclass
class PlayerSkin:
    name: str
    max_health: int
    speed: float
    level: int = 1
    upgrade_cost: int = 150

    def upgrade(self):
        self.level += 1
        self.max_health = int(self.max_health * 1.3)
        self.speed *= 1.1
        self.upgrade_cost = int(self.upgrade_cost * 2)
        return self.upgrade_cost


@dataclass
class Player:
    name: str
    max_health: int
    speed: float
    level: int = 1
    upgrade_cost: int = 150
    current_skin_index: int = 0
    skins: List[PlayerSkin] = None
    
    def __post_init__(self):
        if self.skins is None:
            self.skins = [
                PlayerSkin(name="Солдат", max_health=100, speed=3.0),
                PlayerSkin(name="Бандит", max_health=80, speed=5.0),
                PlayerSkin(name="Джангист", max_health=150, speed=6.0),
            ]
    
    @property
    def current_skin(self):
        return self.skins[self.current_skin_index]

    def upgrade(self):
        self.level += 1
        self.max_health = int(self.max_health * 1.3)
        self.speed *= 1.1
        self.upgrade_cost = int(self.upgrade_cost * 2)
        return self.upgrade_cost



@dataclass
class Bullet:
    x: float
    y: float
    dx: float
    dy: float
    damage: int
    radius: int = 5
    color: arcade.color = arcade.color.YELLOW
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)

@dataclass
class Enemy:
    x: float
    y: float
    health: int
    max_health: int
    speed: float
    radius: int = 20
    color: arcade.color = arcade.color.RED
    
    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    
    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)
        arcade.draw_circle_outline(self.x, self.y, self.radius, arcade.color.BLACK, 2)

        arcade.draw_circle_filled(self.x - 8, self.y + 5, 5, arcade.color.WHITE)
        arcade.draw_circle_filled(self.x + 8, self.y + 5, 5, arcade.color.WHITE)
        arcade.draw_circle_filled(self.x - 8, self.y + 5, 2, arcade.color.BLACK)
        arcade.draw_circle_filled(self.x + 8, self.y + 5, 2, arcade.color.BLACK)

        health_width = 40
        health_ratio = self.health / self.max_health
        arcade.draw_lbwh_rectangle_filled(
            self.x, self.y + self.radius + 15,
            health_width, 5,
            arcade.color.DARK_GRAY
        )
        arcade.draw_lbwh_rectangle_filled(
            self.x - (health_width/2) + (health_width * health_ratio / 2),
            self.y + self.radius + 15,
            health_width * health_ratio, 3,
            arcade.color.GREEN
        )
