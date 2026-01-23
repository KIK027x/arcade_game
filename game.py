import arcade
import os
import time
from level import Level

class Player(arcade.Sprite):
    def __init__(self, skin_name):
        path = os.path.join(os.path.dirname(__file__), "assets", "Players", skin_name, f"alien{skin_name}_front.png")
        super().__init__(path, scale=1.0)
        self.speed_x = 5

class DeathScreen:
    def __init__(self, game_view, time_elapsed, coins_collected):
        self.game_view = game_view
        self.time_elapsed = time_elapsed
        self.coins_collected = coins_collected
        self.hovered = None

    def draw(self):
        w, h = self.game_view.window.width, self.game_view.window.height
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (0, 0, 0, 200))
        arcade.draw_text("СМЕРТЬ", w // 2, h - 150, arcade.color.RED, 48, anchor_x="center")
        arcade.draw_text(f"Время: {self.time_elapsed:.1f} сек", w // 2, h - 220, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text(f"Монеты: {self.coins_collected}", w // 2, h - 260, arcade.color.YELLOW, 24, anchor_x="center")
        arcade.draw_text("🔄 Возродиться", w // 2, h - 350, arcade.color.WHITE, 24, anchor_x="center")

    def on_mouse_press(self, x, y):
        w, h = self.game_view.window.width, self.game_view.window.height
        if abs(x - w // 2) < 150 and abs(y - (h - 350)) < 20:
            self.game_view.restart_level()

class WinScreen:
    def __init__(self, game_view, time_elapsed, coins_collected):
        self.game_view = game_view
        self.time_elapsed = time_elapsed
        self.coins_collected = coins_collected
        self.hovered = None

    def draw(self):
        w, h = self.game_view.window.width, self.game_view.window.height
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (0, 100, 0, 200))
        arcade.draw_text("ПОБЕДА!", w // 2, h - 150, arcade.color.GREEN, 48, anchor_x="center")
        arcade.draw_text(f"Время: {self.time_elapsed:.1f} сек", w // 2, h - 220, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text(f"Монеты: +{self.coins_collected}", w // 2, h - 260, arcade.color.YELLOW, 24, anchor_x="center")
        arcade.draw_text("▶ Продолжить", w // 2, h - 350, arcade.color.WHITE, 24, anchor_x="center")

    def on_mouse_press(self, x, y):
        w, h = self.game_view.window.width, self.game_view.window.height
        if abs(x - w // 2) < 150 and abs(y - (h - 350)) < 20:
            from main_menu import Menu
            menu = Menu()
            self.game_view.window.show_view(menu)

class SettingsMenu:
    def __init__(self, parent_view):
        self.parent_view = parent_view
        self.hovered = None
        self.options = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        from database import get_player_data
        self.death_enabled = get_player_data()["death_screen_enabled"]

    def draw(self):
        w, h = self.parent_view.window.width, self.parent_view.window.height
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (0, 0, 0, 180))
        arcade.draw_text("Настройки", w // 2, h - 150, arcade.color.WHITE, 48, anchor_x="center")

        y = h - 250
        for i, (res_w, res_h) in enumerate(self.options):
            text = f"{res_w}x{res_h}"
            color = arcade.color.YELLOW if (res_w, res_h) == (w, h) else arcade.color.WHITE
            arcade.draw_text(text, w // 2, y, color, 24, anchor_x="center")
            y -= 50

        status = "Вкл" if self.death_enabled else "Выкл"
        arcade.draw_text(f"Экран смерти: {status}", w // 2, y - 20, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("← Назад", w // 2, 50, arcade.color.WHITE, 24, anchor_x="center")

    def on_mouse_motion(self, x, y):
        self.hovered = None
        w, h = self.parent_view.window.width, self.parent_view.window.height
        idx = 0
        for i in range(len(self.options)):
            btn_y = h - 250 - i * 50
            if abs(x - w // 2) < 150 and abs(y - btn_y) < 20:
                self.hovered = ("res", i)
                return
        btn_y = h - 250 - len(self.options) * 50 - 20
        if abs(x - w // 2) < 200 and abs(y - btn_y) < 20:
            self.hovered = ("death", None)
        if abs(x - w // 2) < 100 and abs(y - 50) < 20:
            self.hovered = ("back", None)

    def on_mouse_press(self, x, y):
        w, h = self.parent_view.window.width, self.parent_view.window.height
        if self.hovered:
            kind, val = self.hovered
            if kind == "back":
                self.parent_view.pause_menu.in_settings = False
            elif kind == "res":
                res = self.options[val]
                self.parent_view.window.set_size(*res)
                self.parent_view.window.center_window()
            elif kind == "death":
                self.death_enabled = not self.death_enabled
                from database import set_death_screen
                set_death_screen(self.death_enabled)

class PauseMenu:
    def __init__(self, game_view):
        self.game_view = game_view
        self.hovered = None
        self.buttons = [
            ("▶ Продолжить", self.resume),
            ("⚙ Настройки", self.settings),
            ("🚪 Выйти в меню", self.go_to_main_menu)
        ]
        self.settings_menu = None
        self.in_settings = False

    def draw(self):
        w, h = self.game_view.window.width, self.game_view.window.height
        if self.in_settings:
            self.settings_menu.draw()
        else:
            arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (0, 0, 0, 150))
            arcade.draw_text("ПАУЗА", w // 2, h - 150, arcade.color.WHITE, 48, anchor_x="center")
            y = h - 250
            for i, (text, _) in enumerate(self.buttons):
                x = w // 2
                is_hover = self.hovered == i
                color = arcade.color.YELLOW if is_hover else arcade.color.WHITE
                arcade.draw_text(text, x, y, color, 24, anchor_x="center")
                y -= 60

    def on_mouse_motion(self, x, y):
        w, h = self.game_view.window.width, self.game_view.window.height
        if self.in_settings:
            self.settings_menu.on_mouse_motion(x, y)
        else:
            self.hovered = None
            for i in range(len(self.buttons)):
                btn_y = h - 250 - i * 60
                if abs(x - w // 2) < 150 and abs(y - btn_y) < 20:
                    self.hovered = i
                    break

    def on_mouse_press(self, x, y):
        if self.in_settings:
            self.settings_menu.on_mouse_press(x, y)
        elif self.hovered is not None:
            self.buttons[self.hovered][1]()

    def resume(self):
        self.game_view.paused = False

    def settings(self):
        self.in_settings = True
        self.settings_menu = SettingsMenu(self.game_view)

    def go_to_main_menu(self):
        from main_menu import Menu
        menu = Menu()
        self.game_view.window.show_view(menu)

class GameView(arcade.View):
    def __init__(self, level_path, skin):
        super().__init__()
        self.level_path = level_path
        self.skin = skin
        self.start_time = time.time()
        self.setup()

        # Включаем отслеживание мыши
        self.window.set_mouse_visible(True)

    def setup(self):
        self.level = Level(self.level_path)
        self.player_sprite = Player(self.skin)
        self.player_sprite.center_x = self.window.width // 2
        self.player_sprite.center_y = self.window.height // 2

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.level.platforms,
            gravity_constant=0.5
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.collected_coins = 0
        self.paused = False
        self.pause_menu = PauseMenu(self)
        self.death_screen = None
        self.win_screen = None

    def restart_level(self):
        self.setup()

    def on_draw(self):
        self.clear()
        self.level.draw()
        self.player_list.draw()
        arcade.draw_text(f"Монеты: {self.collected_coins}", 20, self.window.height - 40, arcade.color.YELLOW, 24)

        if self.paused:
            self.pause_menu.draw()
        if self.death_screen:
            self.death_screen.draw()
        if self.win_screen:
            self.win_screen.draw()

    def on_update(self, delta_time):
        if self.death_screen or self.win_screen:
            return

        if not self.paused:
            self.physics_engine.update()

            coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.level.coins)
            for coin in coin_hit_list:
                coin.remove_from_sprite_lists()
                self.collected_coins += 1

            flag_hit = arcade.check_for_collision_with_list(self.player_sprite, self.level.end_flag)
            if flag_hit:
                from database import add_coins
                add_coins(self.collected_coins)
                elapsed = time.time() - self.start_time
                self.win_screen = WinScreen(self, elapsed, self.collected_coins)
                return

            if self.player_sprite.center_y < -100:
                from database import get_player_data
                data = get_player_data()
                if data["death_screen_enabled"]:
                    elapsed = time.time() - self.start_time
                    self.death_screen = DeathScreen(self, elapsed, self.collected_coins)
                else:
                    self.restart_level()

    def on_key_press(self, key, modifiers):
        if self.death_screen or self.win_screen:
            return

        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
            return

        if self.paused:
            return

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -self.player_sprite.speed_x
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = self.player_sprite.speed_x
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = 12

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0

    def on_mouse_motion(self, x, y, dx, dy):
        if self.paused:
            self.pause_menu.on_mouse_motion(x, y)
        elif self.death_screen:
            self.death_screen.on_mouse_motion(x, y)
        elif self.win_screen:
            self.win_screen.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.paused:
            self.pause_menu.on_mouse_press(x, y)
        elif self.death_screen:
            self.death_screen.on_mouse_press(x, y)
        elif self.win_screen:
            self.win_screen.on_mouse_press(x, y)
