import arcade
import os
from level import Level

class Player(arcade.Sprite):
    def __init__(self, skin_name):
        path = os.path.join(os.path.dirname(__file__), "assets", "Players", skin_name, f"alien{skin_name}_front.png")
        super().__init__(path, scale=1.0)
        self.speed_x = 5

class SettingsMenu:
    def __init__(self, parent_view):
        self.parent_view = parent_view
        self.hovered = None
        self.options = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]

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

        # Кнопка Назад
        arcade.draw_text("← Назад", w // 2, 50, arcade.color.WHITE, 24, anchor_x="center")

        arcade.draw_text(f"Текущее: {w}x{h}", w // 2, 100, arcade.color.YELLOW, 20, anchor_x="center")

    def on_mouse_motion(self, x, y):
        self.hovered = None
        w, h = self.parent_view.window.width, self.parent_view.window.height
        for i in range(len(self.options)):
            btn_y = h - 250 - i * 50
            if abs(x - w // 2) < 150 and abs(y - btn_y) < 20:
                self.hovered = i
                break
        # Проверка для кнопки "Назад"
        if abs(x - w // 2) < 100 and abs(y - 50) < 20:
            self.hovered = "back"

    def on_mouse_press(self, x, y):
        w, h = self.parent_view.window.width, self.parent_view.window.height
        if self.hovered == "back":
            self.parent_view.pause_menu.in_settings = False
        elif isinstance(self.hovered, int) and self.hovered is not None:
            w, h = self.options[self.hovered]
            self.parent_view.window.set_size(w, h)
            self.parent_view.window.center_window()

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
        self.level = Level(level_path)
        self.player_sprite = Player(skin)
        # Начальная позиция: по центру экрана
        self.player_sprite.center_x = self.window.width // 2
        self.player_sprite.center_y = self.window.height // 2

        # Используем PhysicsEnginePlatformer для прыжков
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.level.platforms,
            gravity_constant=0.5
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.paused = False
        self.pause_menu = PauseMenu(self)

    def on_draw(self):
        self.clear()
        self.level.draw()
        self.player_list.draw()

        if self.paused:
            self.pause_menu.draw()

    def on_update(self, delta_time):
        if not self.paused:
            self.physics_engine.update()

    def on_key_press(self, key, modifiers):
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

    def on_mouse_press(self, x, y, button, modifiers):
        if self.paused:
            self.pause_menu.on_mouse_press(x, y)