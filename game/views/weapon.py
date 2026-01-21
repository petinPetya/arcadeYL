# views/weapon.py
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
MONEY_COLOR = arcade.color.GOLD


class WeaponSelectView(arcade.View):
    def __init__(self, main_menu_view, user_id: int = 1):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.user_id = user_id
        self.db = main_menu_view.database
        self.user_data = self.db.get_user_data(user_id) or {}
        self.user_stats = self.db.get_user_stats_summary(user_id) or {}
        
        self.buttons = []
        self.arrow_buttons = arcade.SpriteList()
        self.weapons = [
            Weapon("Пистолет", damage=10, fire_rate=0.5),
            Weapon("Дробовик", damage=30, fire_rate=1.2),
            Weapon("Автомат", damage=15, fire_rate=0.2),
            Weapon("Снайперка", damage=50, fire_rate=1.5)
        ]
        self.load_weapon_levels_from_db()
        self.selected_weapon_index = self.get_weapon_index_from_db()
        
        self.init_ui()
    
    def load_weapon_levels_from_db(self):
        weapon_name = self.user_data.get('current_weapon', 'Пистолет')
        weapon_level = self.user_data.get('weapon_level', 1)
        weapon_upgrade_cost = self.user_data.get('weapon_upgrade_cost', 100)
        for weapon in self.weapons:
            if weapon.name == weapon_name:
                weapon.level = weapon_level
                weapon.upgrade_cost = weapon_upgrade_cost
            else:
                weapon.level = 1
                weapon.upgrade_cost = 100
        for weapon in self.weapons:
            weapon.damage = int(weapon.damage * (1 + (weapon.level - 1) * 0.5))
            weapon.fire_rate = max(0.1, weapon.fire_rate * (0.95 ** (weapon.level - 1)))
    
    def get_weapon_index_from_db(self):
        current_weapon = self.user_data.get('current_weapon', 'Пистолет')
        for i, weapon in enumerate(self.weapons):
            if weapon.name == current_weapon:
                return i
        return 0
    
    def init_ui(self):
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
        back_arrow.center_x = 60
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
        arcade.draw_text(
            "АРСЕНАЛ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            bold=True
        )
        money = self.user_stats.get('money', 1000)
        arcade.draw_text(
            f"Денег: {money}$",
            SCREEN_WIDTH - 30,
            SCREEN_HEIGHT - 45,
            MONEY_COLOR,
            28,
            anchor_x="right",
            bold=True
        )
        weapon = self.weapons[self.selected_weapon_index]
        panel_x = SCREEN_WIDTH // 2
        panel_y = SCREEN_HEIGHT // 2

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
            f"СКОРОСТЬ СТРЕЛЬБЫ: {weapon.fire_rate:.2f} выстр/сек",
            f"УРОВЕНЬ: {weapon.level}",
            f"DPS: {weapon.dps:.1f} урона/сек",
            f"СТОИМОСТЬ УЛУЧШЕНИЯ: {weapon.upgrade_cost}"
        ]

        money = self.user_stats.get('money', 1000)
        
        for i, stat in enumerate(stats):
            color = TEXT_COLOR
            if "СТОИМОСТЬ" in stat and money < weapon.upgrade_cost:
                color = arcade.color.RED
            
            arcade.draw_text(
                stat,
                panel_x - 250,
                stats_y - 100 - i * 35,
                color,
                20
            )

        for x, y, width, height, text, _ in self.buttons:
            if text == "УЛУЧШИТЬ" and money < weapon.upgrade_cost:
                button_color = arcade.color.DARK_GRAY
                text_color = arcade.color.GRAY
            else:
                button_color = BUTTON_COLOR
                text_color = TEXT_COLOR
            arcade.draw_text(
                text, x, y, text_color, 20,
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

        current_weapon_name = self.user_data.get('current_weapon', 'Пистолет')
        if weapon.name == current_weapon_name:
            arcade.draw_text(
                "ТЕКУЩЕЕ ОРУЖИЕ",
                panel_x,
                panel_y + 150,
                arcade.color.GREEN,
                24,
                anchor_x="center",
                bold=True
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
                (center_x - size - 20,  center_y),
                (center_x + size - 20, center_y - size),
                (center_x + size - 20, center_y + size)
            ]
        elif direction == "right":
            return [
                (center_x + size + 20 , center_y),
                (center_x - size + 20, center_y - size),
                (center_x - size + 20, center_y + size)
            ]
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn_x, btn_y, width, height, text, action in self.buttons:
                if (btn_x - width/2 < x < btn_x + width/2 and 
                    btn_y - height/2 < y < btn_y + height/2):
                    if text == "УЛУЧШИТЬ":
                        weapon = self.weapons[self.selected_weapon_index]
                        money = self.user_stats.get('money', 1000)
                        if money >= weapon.upgrade_cost:
                            action()
                    else:
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
        selected_weapon = self.weapons[self.selected_weapon_index]
        self.db.update_user_settings(
            self.user_id,
            current_weapon=selected_weapon.name,
            weapon_level=selected_weapon.level,
            weapon_upgrade_cost=selected_weapon.upgrade_cost
        )
        self.user_data['current_weapon'] = selected_weapon.name
        
        print(f"Выбрано оружие: {selected_weapon.name} (Уровень {selected_weapon.level})")
        self.go_back()
    
    def upgrade_current(self):
        weapon = self.weapons[self.selected_weapon_index]
        money = self.user_stats.get('money', 1000)
        
        if money >= weapon.upgrade_cost:
            new_money = money - weapon.upgrade_cost

            old_dps = weapon.dps
            weapon.upgrade()
            new_dps = weapon.dps
            self.db.update_user_settings(
                self.user_id,
                money=new_money,
                weapon_level=weapon.level,
                weapon_upgrade_cost=weapon.upgrade_cost
            )
            self.user_stats['money'] = new_money
            
            print(f"Оружие {weapon.name} улучшено до уровня {weapon.level}")
            print(f"DPS улучшился с {old_dps:.1f} до {new_dps:.1f}")
            print(f"Осталось денег: {new_money}")
        else:
            print(f"Недостаточно денег! Нужно: {weapon.upgrade_cost}, есть: {money}")
    
    def go_back(self):
        self.window.show_view(self.main_menu_view)
