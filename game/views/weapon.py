import arcade
from data import Weapon

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "2D Shooter Arena"

ARSENAL_BACKGROUND = arcade.color.DARK_SLATE_GRAY
PANEL_COLOR = arcade.color.DARK_BLUE_GRAY
ACCENT_COLOR = arcade.color.GOLDEN_YELLOW
TEXT_COLOR = arcade.color.WHITE_SMOKE
BUTTON_COLOR = arcade.color.DARK_BLUE


class WeaponSelectView(arcade.View):
    def __init__(self, main_menu_view):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.buttons = []
        self.arrow_buttons = arcade.SpriteList()
        self.weapons = [
            Weapon("Пистолет", damage=10, fire_rate=0.5),
            Weapon("Дробовик", damage=30, fire_rate=1.2),
            Weapon("Автомат", damage=15, fire_rate=0.2),
            Weapon("Снайперка", damage=50, fire_rate=1.5)
        ]
        self.selected_weapon_index = 0
        self.init_ui()
    
    def init_ui(self):
        # Координаты для кнопок
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        button_y = 150
        button_spacing = 200
        self.buttons = [
            (center_x - button_spacing, button_y, 200, 50, "ВЫБРАТЬ", self.select_current),
            (center_x + button_spacing, button_y, 200, 50, "УЛУЧШИТЬ", self.upgrade_current),
        ]
        self.create_arrow_buttons()
    
    def create_arrow_buttons(self):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        back_arrow = arcade.SpriteSolidColor(80, 80, arcade.color.TRANSPARENT_BLACK)
        back_arrow.center_x = 60  # Отступ слева
        back_arrow.center_y = SCREEN_HEIGHT - 60
        back_arrow.width = 80
        back_arrow.height = 80
        back_arrow.action = self.go_back
        back_arrow.name = "back"

        left_arrow = arcade.SpriteSolidColor(100, 100, arcade.color.TRANSPARENT_BLACK)
        left_arrow.center_x = center_x - 150
        left_arrow.center_y = center_y + 100
        left_arrow.width = 100
        left_arrow.height = 100
        left_arrow.action = self.prev_weapon
        left_arrow.name = "left"
        right_arrow = arcade.SpriteSolidColor(100, 100, arcade.color.TRANSPARENT_BLACK)
        right_arrow.center_x = center_x + 150
        right_arrow.center_y = center_y + 100
        right_arrow.width = 100
        right_arrow.height = 100
        right_arrow.action = self.next_weapon
        right_arrow.name = "right"

        self.arrow_buttons.append(back_arrow)
        self.arrow_buttons.append(left_arrow)
        self.arrow_buttons.append(right_arrow)
    
    def on_draw(self):
        self.clear()
        arcade.set_background_color(ARSENAL_BACKGROUND)

        arcade.draw_lbwh_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_HEIGHT - 100,
            arcade.color.DARK_SLATE_BLUE
        )
        arcade.draw_text(
            "АРСЕНАЛ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            bold=True
        )

        weapon = self.weapons[self.selected_weapon_index]
        panel_x = SCREEN_WIDTH // 2
        panel_y = SCREEN_HEIGHT // 2

        # Название оружия
        arcade.draw_text(
            weapon.name,
            panel_x,
            panel_y + 100,
            ACCENT_COLOR,
            36,
            anchor_x="center",
            bold=True
        )

        stats_y = panel_y + 40
        stats = [
            f"УРОН: {weapon.damage}",
            f"СКОРОСТЬ СТРЕЛЬБЫ: {weapon.fire_rate:.1f}",
            f"УРОВЕНЬ: {weapon.level}",
            f"СТОИМОСТЬ УЛУЧШЕНИЯ: {weapon.upgrade_cost}"
        ]
        
        for i, stat in enumerate(stats):
            arcade.draw_text(
                stat,
                panel_x - 200,
                stats_y - 100 - i * 40,
                TEXT_COLOR,
                20
            )

        for x, y, width, height, text, _ in self.buttons:
            arcade.draw_text(
                text, x, y, TEXT_COLOR, 20,
                anchor_x="center", anchor_y="center",
                bold=True
            )

        for sprite in self.arrow_buttons:
            if sprite.name == "back":
                self.draw_back_button(sprite.center_x, sprite.center_y)
            elif sprite.name == "left":
                points = self.create_arrow_points(sprite.center_x, sprite.center_y, "left")
                arcade.draw_polygon_filled(points, ACCENT_COLOR)
                arcade.draw_polygon_outline(points, TEXT_COLOR, line_width=2)

                arcade.draw_text(
                    "Предыдущее",
                    sprite.center_x,
                    sprite.center_y - 70,
                    TEXT_COLOR,
                    16,
                    anchor_x="center"
                )
            elif sprite.name == "right":
                points = self.create_arrow_points(sprite.center_x, sprite.center_y, "right")
                arcade.draw_polygon_filled(points, ACCENT_COLOR)
                arcade.draw_polygon_outline(points, TEXT_COLOR, line_width=2)
                arcade.draw_text(
                    "Следующее",
                    sprite.center_x,
                    sprite.center_y - 70,
                    TEXT_COLOR,
                    16,
                    anchor_x="center"
                )
    
    def draw_back_button(self, x, y):
        points = self.create_arrow_points(x, y, "left")
        arcade.draw_polygon_filled(points, ACCENT_COLOR)
        arcade.draw_polygon_outline(points, TEXT_COLOR, line_width=2)

        arcade.draw_text(
            "Назад",
            x + 50,
            y,
            TEXT_COLOR,
            20,
            anchor_x="left",
            anchor_y="center",
            bold=True
        )
    
    def create_arrow_points(self, center_x, center_y, direction, size=30):
        if direction == "left":
            return [
                (center_x + size, center_y),
                (center_x - size, center_y - size),
                (center_x - size, center_y + size)
            ]
        elif direction == "right":
            return [
                (center_x - size, center_y),
                (center_x + size, center_y - size),
                (center_x + size, center_y + size)
            ]
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn_x, btn_y, width, height, text, action in self.buttons:
                if (btn_x - width/2 < x < btn_x + width/2 and 
                    btn_y - height/2 < y < btn_y + height/2):
                    action()

            for sprite in self.arrow_buttons:
                if (sprite.center_x - sprite.width/2 < x < sprite.center_x + sprite.width/2 and
                    sprite.center_y - sprite.height/2 < y < sprite.center_y + sprite.height/2):
                    sprite.action()
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.prev_weapon()
        elif key == arcade.key.RIGHT:
            self.next_weapon()
        elif key == arcade.key.ENTER:
            self.select_current()
        elif key == arcade.key.ESCAPE:
            self.go_back()
        elif key == arcade.key.U:
            self.upgrade_current()
        elif key == arcade.key.B:
            self.go_back()
    
    def prev_weapon(self):
        self.selected_weapon_index = (self.selected_weapon_index - 1) % len(self.weapons)
    
    def next_weapon(self):
        self.selected_weapon_index = (self.selected_weapon_index + 1) % len(self.weapons)
    
    def select_current(self):
        if hasattr(self.main_menu_view, 'current_weapon_index'):
            self.main_menu_view.current_weapon_index = self.selected_weapon_index
        print(f"Выбрано оружие: {self.weapons[self.selected_weapon_index].name}")
        self.go_back()
    
    def upgrade_current(self):
        weapon = self.weapons[self.selected_weapon_index]
        if hasattr(self.main_menu_view, 'player_money'):
            if self.main_menu_view.player_money >= weapon.upgrade_cost:
                self.main_menu_view.player_money -= weapon.upgrade_cost
                weapon.upgrade()
                print(f"Оружие {weapon.name} улучшено до уровня {weapon.level}")
            else:
                print(f"Недостаточно денег! Нужно: {weapon.upgrade_cost}")
        else:
            weapon.upgrade()
            print(f"Оружие {weapon.name} улучшено до уровня {weapon.level}")
    
    def go_back(self):
        self.window.show_view(self.main_menu_view)
