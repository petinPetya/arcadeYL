import arcade
from dataclasses import dataclass

from database import Database
from views import weapon, player, game, profile  # views.py, привет джанга!


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
        self.current_user = None
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
                "БОЙЦЫ",
                self.switch_to_player,
            ),
            (
                center_x,
                center_y,
                button_width,
                button_height,
                "АРСЕНАЛ",
                self.switch_to_weapon,
            ),
            (
                center_x,
                center_y - 60,
                button_width,
                button_height,
                "РЕКОРДЫ",
                self.show_scores,
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
        elif key == arcade.key.RIGHT:
            self.next_weapon()
        elif key == arcade.key.LEFT:
            self.next_skin()

    def start_game(self):
        game_view = game.GameView(
            self.skins[self.current_skin_index],
            weapon.WeaponSelectView.weapons[0],
            self.database,
        )
        self.window.show_view(game_view)

    def show_scores(self):
        pr_view = profile.ProfileView(
            
        )

    def switch_to_weapon(self):
        weapon_view = weapon.WeaponSelectView(self)
        self.window.show_view(weapon_view)

    def switch_to_player(self):
        weapon_view = player.PlayerSelectView(self)
        self.window.show_view(weapon_view)

    def exit_game(self):
        arcade.close_window()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    ## arcade.open_window(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 500, SCREEN_TITLE)
    db = Database()
    db.create_user("Player1")

    menu_view = MainMenuView(db)
    window.show_view(menu_view)

    arcade.run()
    db.close()
