import arcade

from database import Database
from views.weapon import WeaponSelectView
from views.player import PlayerSelectView
from views.game import GameView
from views.profile import ProfileView

from data import PlayerSkin

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "2D Shooter Arena"

MENU_BACKGROUND = arcade.color.DARK_SLATE_GRAY
PANEL_COLOR = arcade.color.DARK_BLUE_GRAY
ACCENT_COLOR = arcade.color.GOLDEN_YELLOW
TEXT_COLOR = arcade.color.WHITE_SMOKE


class MainMenuView(arcade.View):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.current_user = 1
        self.buttons = []
        self.init_ui()

    def init_ui(self):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        button_width = 300
        button_height = 50
        spacing = 20
        self.buttons = [
            (
                center_x,
                center_y + 120,
                button_width,
                button_height,
                "НАЧАТЬ ИГРУ",
                self.start_game,
            ),
            (
                center_x,
                center_y + 60,
                button_width,
                button_height,
                "ПРОФИЛЬ",
                self.show_profile,
            ),
            (
                center_x,
                center_y,
                button_width,
                button_height,
                "БОЙЦЫ",
                self.switch_to_player,
            ),
            (
                center_x,
                center_y - 60,
                button_width,
                button_height,
                "АРСЕНАЛ",
                self.switch_to_weapon,
            ),
            (
                center_x,
                center_y - 120,
                button_width,
                button_height,
                "ВЫХОД",
                self.exit_game,
            ),
        ]

    def on_draw(self):
        self.clear()
        arcade.set_background_color(MENU_BACKGROUND)
        
        arcade.draw_text(
            "2D SHOOTER ARENA",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            font_name="Arial",
            bold=True,
        )

        for x, y, width, height, text, _ in self.buttons:
            arcade.draw_text(
                text,
                x,
                y,
                TEXT_COLOR,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name="Arial",
                bold=True,
            )

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn_x, btn_y, width, height, text, action in self.buttons:
                if (
                    btn_x - width / 2 < x < btn_x + width / 2
                    and btn_y - height / 2 < y < btn_y + height / 2
                ):
                    action()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.start_game()
        elif key == arcade.key.ESCAPE:
            self.exit_game()
        elif key == arcade.key.P:
            self.switch_to_player()
        elif key == arcade.key.W:
            self.switch_to_weapon()
        elif key == arcade.key.P:
            self.show_profile()

    def start_game(self):
        user_data = self.database.get_user_data(self.current_user) or {}
        current_skin = user_data.get('current_skin', 'Солдат')

        if current_skin == "Солдат":
            skin = PlayerSkin(name="Солдат", max_health=100, speed=3.0)
        elif current_skin == "Бандит":
            skin = PlayerSkin(name="Бандит", max_health=80, speed=5.0)
        else:
            skin = PlayerSkin(name="Джангист", max_health=1500, speed=6.0)

        from data import Weapon
        weapon = Weapon("Пистолет", damage=10, fire_rate=0.5)

        game_view = GameView(self, self.current_user)
        self.window.show_view(game_view)

    def show_profile(self):
        profile_view = ProfileView(self)
        self.window.show_view(profile_view)

    def switch_to_weapon(self):
        weapon_view = WeaponSelectView(self)
        self.window.show_view(weapon_view)

    def switch_to_player(self):
        player_view = PlayerSelectView(self, self.current_user)
        self.window.show_view(player_view)

    def exit_game(self):
        arcade.close_window()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    db = Database()
    db.create_user("Player1")

    menu_view = MainMenuView(db)
    window.show_view(menu_view)

    arcade.run()
    db.close()


if __name__ == "__main__":
    main()
