import arcade
from data import Player, PlayerSkin

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
PANEL_COLOR = arcade.color.DARK_BLUE_GRAY
ACCENT_COLOR = arcade.color.GOLDEN_YELLOW
TEXT_COLOR = arcade.color.WHITE_SMOKE
MONEY_COLOR = arcade.color.GOLD


class ProfileView(arcade.View):
    def __init__(self, main_menu_view, user_id: int = 1):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.user_id = user_id
        self.db = main_menu_view.database
        self.user_data = self.db.get_user_data(user_id) or {}
        self.user_stats = self.db.get_user_stats_summary(user_id) or {}
        self.recent_records = self.db.get_user_recent_records(user_id, 5)

        skin_name = self.user_data.get('current_skin', 'Солдат')
        skin_level = self.user_data.get('skin_level', 1)
        if skin_name == "Солдат":
            self.current_skin = PlayerSkin(name="Солдат", max_health=100, speed=3.0)
        elif skin_name == "Бандит":
            self.current_skin = PlayerSkin(name="Бандит", max_health=80, speed=5.0)
        else:
            self.current_skin = PlayerSkin(name="Джангист", max_health=150, speed=6.0)
        self.current_skin.level = skin_level
        self.calculate_upgraded_stats()
        self.current_weapon = self.user_data.get('current_weapon', 'Пистолет')
        
        self.buttons = []
        self.init_ui()
    
    def calculate_upgraded_stats(self):
        base_health = self.current_skin.max_health
        base_speed = self.current_skin.speed
        health_multiplier = 1.0 + (self.current_skin.level - 1) * 0.3
        speed_multiplier = 1.0 + (self.current_skin.level - 1) * 0.1
        
        self.current_health = int(base_health * health_multiplier)
        self.current_speed = base_speed * speed_multiplier
    
    def init_ui(self):
        self.back_button = arcade.SpriteSolidColor(100, 60, arcade.color.TRANSPARENT_BLACK)
        self.back_button.center_x = 100
        self.back_button.center_y = SCREEN_HEIGHT - 40
        self.change_skin_button = arcade.SpriteSolidColor(200, 60, arcade.color.TRANSPARENT_BLACK)
        self.change_skin_button.center_x = SCREEN_WIDTH // 2
        self.change_skin_button.center_y = 100
    
    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.draw_header()
        self.draw_player_stats()
        self.draw_skin_info()
        self.draw_records_and_progress()
        self.draw_buttons()
    
    def draw_header(self):
        arcade.draw_text(
            f"{self.user_data.get('username', 'Анонимус дима')}",
            SCREEN_WIDTH / 2 - 60,
            SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            28,
            bold=True
        )
        level = self.user_stats.get('skin_level', 1)
        money = self.user_stats.get('money', 1000)
        arcade.draw_text(
            f"Денег: {money}$",
            SCREEN_WIDTH - 30,
            SCREEN_HEIGHT - 60,
            MONEY_COLOR,
            28,
            anchor_x="right",
            bold=True
        )
    
    def draw_player_stats(self):
        panel_x = SCREEN_WIDTH // 4
        panel_y = SCREEN_HEIGHT // 2
        arcade.draw_lbwh_rectangle_filled(
            panel_x - 200, panel_y - 250, 400, 500,
            PANEL_COLOR
        )
        arcade.draw_text(
            "СТАТИСТИКА",
            panel_x - 20, panel_y + 220,
            ACCENT_COLOR, 24,
            anchor_x="center", bold=True
        )

        stats = [
            f"Рекорд: {self.user_stats.get('high_score', 0)}",
            f"Всего убийств: {self.user_stats.get('total_kills', 0)}",
            f"Игр сыграно: {self.user_stats.get('games_played', 0)}",
            f"Общее время: {self.user_stats.get('total_play_time', 0) // 60} мин",
            f"Убийств/игра: {self.calculate_kills_per_game():.1f}",
            f"Очков/игра: {self.calculate_score_per_game():.0f}",
            f"Текущее оружие: {self.current_weapon}",
            f"Всего заработано: {self.calculate_total_earned()}"
        ]
        
        start_y = panel_y + 170
        for i, stat in enumerate(stats[:6]):
            arcade.draw_text(
                stat,
                panel_x - 180,
                start_y - i * 35,
                TEXT_COLOR, 18
            )
        for i, stat in enumerate(stats[6:], start=6):
            arcade.draw_text(
                stat,
                panel_x - 180,
                panel_y - 80 - (i - 6) * 35,
                TEXT_COLOR, 18
            )
    
    def draw_skin_info(self):
        panel_x = SCREEN_WIDTH // 2
        panel_y = SCREEN_HEIGHT // 2
        arcade.draw_lbwh_rectangle_filled(
            panel_x - 200, panel_y - 250, 400, 500,
            PANEL_COLOR
        )
        arcade.draw_text(
            "ВАШ БОЕЦ",
            panel_x, panel_y + 220,
            ACCENT_COLOR, 24,
            anchor_x="center", bold=True
        )
        avatar_y = panel_y + 140
        arcade.draw_circle_filled(panel_x, avatar_y, 80, arcade.color.LIGHT_GRAY)
        arcade.draw_circle_outline(panel_x, avatar_y, 80, ACCENT_COLOR, 4)

        if self.current_skin.name == "Солдат":
            skin_color = arcade.color.ARMY_GREEN
            hat_color = arcade.color.DARK_GREEN
        elif self.current_skin.name == "Бандит":
            skin_color = arcade.color.DARK_RED
            hat_color = arcade.color.DARK_RED
        else:
            skin_color = arcade.color.DARK_BLUE
            hat_color = arcade.color.DARK_BLUE

        arcade.draw_circle_filled(panel_x, avatar_y, 60, skin_color)
        head_y = avatar_y + 40
        arcade.draw_circle_filled(panel_x, head_y, 25, arcade.color.PEACH)
        arcade.draw_circle_outline(panel_x, head_y, 25, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(panel_x, head_y + 15, 30, hat_color)

        arcade.draw_circle_filled(panel_x - 10, head_y + 5, 5, arcade.color.WHITE)
        arcade.draw_circle_filled(panel_x + 10, head_y + 5, 5, arcade.color.WHITE)
        arcade.draw_circle_filled(panel_x - 10, head_y + 5, 2, arcade.color.BLACK)
        arcade.draw_circle_filled(panel_x + 10, head_y + 5, 2, arcade.color.BLACK)

        arcade.draw_arc_filled(panel_x, head_y - 10, 15, 8, arcade.color.DARK_RED, 0, 180)

        arcade.draw_text(
            self.current_skin.name,
            panel_x,
            avatar_y - 100,
            ACCENT_COLOR,
            32,
            anchor_x="center",
            bold=True
        )

        arcade.draw_text(
            f"Уровень {self.current_skin.level}",
            panel_x,
            avatar_y - 130,
            arcade.color.GOLD,
            24,
            anchor_x="center"
        )
        stats_start_y = avatar_y - 170
        skin_stats = [
            f"Здоровье: {self.current_health}",
            f"Скорость: {self.current_speed:.1f}",
            f"Бонус урона: +{self.calculate_damage_bonus():.0f}%",
            f"Бонус защиты: +{self.calculate_defense_bonus():.0f}%"
        ]
        
        for i, stat in enumerate(skin_stats):
            arcade.draw_text(
                stat,
                panel_x - 180,
                stats_start_y - i * 35,
                TEXT_COLOR, 20,
                bold=True if i < 2 else False
            )
        upgrade_cost = self.current_skin.upgrade_cost
        money = self.user_stats.get('money', 1000)

        arcade.draw_text(
            f"След. улучшение: {upgrade_cost}",
            panel_x - 180,
            stats_start_y - 4 * 35,
            arcade.color.RED if money < upgrade_cost else arcade.color.GREEN,
            18
        )
    
    def draw_records_and_progress(self):
        panel_x = 3 * SCREEN_WIDTH // 4
        panel_y = SCREEN_HEIGHT // 2

        arcade.draw_lbwh_rectangle_filled(
            panel_x - 200, panel_y - 250, 400, 500,
            PANEL_COLOR
        )

        arcade.draw_text(
            "РЕКОРДЫ",
            panel_x, panel_y + 220,
            ACCENT_COLOR, 24,
            anchor_x="center", bold=True
        )
        if self.recent_records:
            start_y = panel_y + 170
            for i, record in enumerate(self.recent_records[:5]):
                arcade.draw_lbwh_rectangle_filled(
                    panel_x - 180, start_y - i * 60 - 20,
                    360, 50,
                    arcade.color.DARK_SLATE_GRAY if i % 2 == 0 else arcade.color.DARK_BLUE_GRAY
                )
                arcade.draw_text(
                    f"{i+1}.",
                    panel_x - 170,
                    start_y - i * 60,
                    ACCENT_COLOR, 18,
                    bold=True
                )
                arcade.draw_text(
                    f"{record['score']} очков",
                    panel_x - 140,
                    start_y - i * 60 + 10,
                    TEXT_COLOR, 16
                )
                
                arcade.draw_text(
                    f"{record.get('kills', 0)} убийств",
                    panel_x - 140,
                    start_y - i * 60 - 10,
                    arcade.color.LIGHT_GRAY, 14
                )
                play_time = record.get('play_time', 0)
                arcade.draw_text(
                    f"{play_time // 60}:{play_time % 60:02d}",
                    panel_x + 100,
                    start_y - i * 60,
                    arcade.color.LIGHT_GRAY, 14,
                    anchor_x="right"
                )
        else:
            arcade.draw_text(
                "Пока нет рекордов",
                panel_x, panel_y,
                TEXT_COLOR, 20,
                anchor_x="center", anchor_y="center"
            )
        self.draw_level_progress(panel_x, panel_y - 200)
    
    def draw_level_progress(self, panel_x, start_y):
        arcade.draw_text(
            "УРОВЕНЬ",
            panel_x, start_y + 50,
            ACCENT_COLOR, 20,
            anchor_x="center", bold=True
        )
        current_level = self.current_skin.level
        arcade.draw_lbwh_rectangle_filled(
            panel_x - 150, start_y - 15,
            300, 20,
            arcade.color.DARK_GRAY
        )

        progress_ratio = 0.6
        arcade.draw_lbwh_rectangle_filled(
            panel_x - 150, start_y - 15,
            300 * progress_ratio, 20,
            arcade.color.GREEN
        )
        arcade.draw_text(
            f"Уровень {current_level} -> {current_level + 1}",
            panel_x, start_y + 15,
            TEXT_COLOR, 16,
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"{int(progress_ratio * 100)}%",
            panel_x, start_y - 30,
            arcade.color.WHITE, 16,
            anchor_x="center", anchor_y="center"
        )
    
    def draw_buttons(self):
        arcade.draw_text(
            "Назад",
            self.back_button.center_x,
            self.back_button.center_y,
            TEXT_COLOR, 20,
            anchor_x="center", anchor_y="center",
            bold=True
        )
        arcade.draw_text(
            "СМЕНИТЬ СКИН",
            self.change_skin_button.center_x,
            self.change_skin_button.center_y,
            TEXT_COLOR, 22,
            anchor_x="center", anchor_y="center",
            bold=True
        )
    
    def calculate_kills_per_game(self):
        games_played = self.user_stats.get('games_played', 0)
        total_kills = self.user_stats.get('total_kills', 0)
        
        if games_played > 0:
            return total_kills / games_played
        return 0.0
    
    def calculate_score_per_game(self):
        games_played = self.user_stats.get('games_played', 0)
        total_score = self.user_stats.get('total_score', 0)
        
        if games_played > 0:
            return total_score / games_played
        return 0
    
    # вот эти геттеры сеттеры можно было бы ломбоком делать
    def calculate_total_earned(self):
        current_money = self.user_stats.get('money', 1000)
        return max(0, current_money - 1000)
    
    def calculate_damage_bonus(self):
        return (self.current_skin.level - 1) * 10
    
    def calculate_defense_bonus(self):
        return (self.current_skin.level - 1) * 5
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if (self.back_button.center_x - 50 <= x <= self.back_button.center_x + 50 and
                self.back_button.center_y - 30 <= y <= self.back_button.center_y + 30):
                self.window.show_view(self.main_menu_view)

            elif (self.change_skin_button.center_x - 100 <= x <= self.change_skin_button.center_x + 100 and
                  self.change_skin_button.center_y - 30 <= y <= self.change_skin_button.center_y + 30):
                from views.player import PlayerSelectView
                player_select_view = PlayerSelectView(self.main_menu_view, self.user_id)
                self.window.show_view(player_select_view)
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.B:
            self.window.show_view(self.main_menu_view)
        elif key == arcade.key.S:
            from views.player import PlayerSelectView
            player_select_view = PlayerSelectView(self.main_menu_view, self.user_id)
            self.window.show_view(player_select_view)
