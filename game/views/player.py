# views/player.py
import arcade
from data import PlayerSkin

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "2D Shooter Arena"

ARSENAL_BACKGROUND = arcade.color.DARK_SLATE_GRAY
PANEL_COLOR = arcade.color.DARK_BLUE_GRAY
ACCENT_COLOR = arcade.color.GOLDEN_YELLOW
TEXT_COLOR = arcade.color.WHITE_SMOKE
BUTTON_COLOR = arcade.color.DARK_BLUE
MONEY_COLOR = arcade.color.GOLD


class PlayerSelectView(arcade.View):
    def __init__(self, main_menu_view, user_id: int = 1):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.user_id = user_id
        self.db = main_menu_view.database
        self.user_data = self.db.get_user_data(user_id) or {}
        self.user_stats = self.db.get_user_stats_summary(user_id) or {}
        
        self.buttons = []
        self.arrow_buttons = arcade.SpriteList()
        self.skins = [
            PlayerSkin(name="Солдат", max_health=100, speed=3.0),
            PlayerSkin(name="Бандит", max_health=80, speed=5.0),
            PlayerSkin(name="Джангист", max_health=150, speed=6.0),
        ]
        skin_level = self.user_data.get('skin_level', 1)
        for skin in self.skins:
            skin.level = skin_level
        
        self.selected_skin_index = self.get_skin_index_from_db()
        self.init_ui()
    
    def get_skin_index_from_db(self):
        current_skin = self.user_data.get('current_skin', 'Солдат')
        for i, skin in enumerate(self.skins):
            if skin.name == current_skin:
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
        left_arrow.action = self.prev_skin
        left_arrow.name = "left"
        right_arrow = arcade.SpriteSolidColor(100, 100, arcade.color.TRANSPARENT_BLACK)
        right_arrow.center_x = center_x + 150
        right_arrow.center_y = center_y + 100
        right_arrow.width = 100
        right_arrow.height = 100
        right_arrow.action = self.next_skin
        right_arrow.name = "right"

        self.arrow_buttons.append(back_arrow)
        self.arrow_buttons.append(left_arrow)
        self.arrow_buttons.append(right_arrow)
    
    def on_draw(self):
        self.clear()
        arcade.set_background_color(ARSENAL_BACKGROUND)

        arcade.draw_text(
            "ВЫБОР ПЕРСОНАЖА",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            bold=True
        )

        money = self.user_stats.get('money', 0)
        arcade.draw_text(
            f"Денег: {money}$",
            SCREEN_WIDTH - 10,
            SCREEN_HEIGHT - 45,
            TEXT_COLOR,
            28,
            anchor_x="right",
            bold=True
        )

        skin = self.skins[self.selected_skin_index]
        panel_x = SCREEN_WIDTH // 2
        panel_y = SCREEN_HEIGHT // 2

        arcade.draw_text(
            skin.name,
            panel_x,
            panel_y + 100,
            ACCENT_COLOR,
            36,
            anchor_x="center",
            bold=True
        )
        current_skin_name = self.user_data.get('current_skin', 'Бандит')
        if skin.name == current_skin_name:
            arcade.draw_text(
                "ТЕКУЩИЙ СКИН",
                panel_x,
                panel_y + 150,
                arcade.color.GREEN,
                24,
                anchor_x="center",
                bold=True
            )
        stats_y = panel_y + 40
        stats = [
            f"ЗДОРОВЬЕ: {skin.max_health}",
            f"СКОРОСТЬ: {skin.speed:.1f}",
            f"УРОВЕНЬ: {skin.level}",
            f"СТОИМОСТЬ УЛУЧШЕНИЯ: {skin.upgrade_cost}"
        ]
        
        for i, stat in enumerate(stats):
            color = TEXT_COLOR
            if "СТОИМОСТЬ" in stat:
                if money < skin.upgrade_cost:
                    color = arcade.color.RED
            
            arcade.draw_text(
                stat,
                panel_x - 200,
                stats_y - 100 - i * 40,
                color,
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
                    "Предыдущий",
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
                    "Следующий",
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
                    action()
            for sprite in self.arrow_buttons:
                if (sprite.center_x - sprite.width/2 < x < sprite.center_x + sprite.width/2 and
                    sprite.center_y - sprite.height/2 < y < sprite.center_y + sprite.height/2):
                    sprite.action()
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.prev_skin()
        elif key == arcade.key.RIGHT:
            self.next_skin()
        elif key == arcade.key.ENTER:
            self.select_current()
        elif key == arcade.key.ESCAPE:
            self.go_back()
        elif key == arcade.key.U:
            self.upgrade_current()
        elif key == arcade.key.B:
            self.go_back()
    
    def prev_skin(self):
        self.selected_skin_index = (self.selected_skin_index - 1) % len(self.skins)
    
    def next_skin(self):
        self.selected_skin_index = (self.selected_skin_index + 1) % len(self.skins)
    
    def select_current(self):
        selected_skin = self.skins[self.selected_skin_index]
        self.db.update_user_settings(
            self.user_id,
            current_skin=selected_skin.name,
            skin_level=selected_skin.level,
            skin_upgrade_cost=selected_skin.upgrade_cost
        )
        
        print(f"Выбран персонаж: {selected_skin.name}")
        self.go_back()
    
    def upgrade_current(self):
        skin = self.skins[self.selected_skin_index]
        money = self.user_stats.get('money', 1000)
        
        if money >= skin.upgrade_cost:
            new_money = money - skin.upgrade_cost
            skin.upgrade()
            self.db.update_user_settings(
                self.user_id,
                money=new_money,
                skin_level=skin.level,
                skin_upgrade_cost=skin.upgrade_cost
            )
            self.user_stats['money'] = new_money
            
            print(f"Персонаж {skin.name} улучшен до уровня {skin.level}")
        else:
            print(f"Недостаточно денег! Нужно: {skin.upgrade_cost}, есть: {money}")
    
    def go_back(self):
        self.window.show_view(self.main_menu_view)
