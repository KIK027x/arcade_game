import arcade
import os

# Константы
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Platformer - Главное меню"

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        # Загрузка текстур
        self.bg = arcade.load_texture(os.path.join(ASSETS_PATH, "Backgrounds", "blue_grass.png"))

        # Кнопки
        self.button_normal = arcade.load_texture(os.path.join(ASSETS_PATH, "HUD", "hudJewel_red_empty.png"))
        self.button_hover = arcade.load_texture(os.path.join(ASSETS_PATH, "HUD", "hudJewel_red.png"))

        self.current_view = "main"  # main, levels, skins, settings
        self.hovered_button = None
        self.selected_skin = "Beige"  # Имя папки
        self.selected_level = 1
        self.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)

        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1920, 1080)
        ]
        # Скины
        self.skins = ["Бежевый", "Голубой", "Зеленый"]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        self.clear()
        # Растянуть фон
        arcade.draw_texture_rect(
            self.bg,
            rect=arcade.LBWH(
                SCREEN_WIDTH // 2 - self.bg.width // 2,
                SCREEN_HEIGHT // 2 - self.bg.height // 2,
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            ),
            color=arcade.color.WHITE,
            alpha=255
        )

        arcade.draw_text(
            "Platformer", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.WHITE, 48, anchor_x="center", font_name="Arial"
        )

        if self.current_view == "main":
            self.draw_main_menu()
        elif self.current_view == "levels":
            self.draw_levels_menu()
        elif self.current_view == "skins":
            self.draw_skins_menu()
        elif self.current_view == "settings":
            self.draw_settings_menu()

    def draw_main_menu(self):
        buttons = [
            ("Играть", self.start_game),
            ("Уровни", lambda: setattr(self, 'current_view', 'levels')),
            ("Скины", lambda: setattr(self, 'current_view', 'skins')),
            ("Настройки", lambda: setattr(self, 'current_view', 'settings')),
            ("Выход", arcade.exit)
        ]
        self.draw_buttons(buttons, start_y=SCREEN_HEIGHT - 200, spacing=80)

    def draw_levels_menu(self):
        arcade.draw_text("Выберите уровень", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        level_buttons = [(f"Уровень {i}", lambda lvl=i: setattr(self, 'selected_level', lvl)) for i in range(1, 6)]
        level_buttons.append(("Назад", lambda: setattr(self, 'current_view', 'main')))
        self.draw_buttons(level_buttons, start_y=SCREEN_HEIGHT - 220, spacing=60)

    def draw_skins_menu(self):
        arcade.draw_text("Выберите героя", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        skin_buttons = [(s, lambda s_name=s: setattr(self, 'selected_skin', s_name)) for s in self.skins]
        skin_buttons.append(("Назад", lambda: setattr(self, 'current_view', 'main')))
        self.draw_buttons(skin_buttons, start_y=SCREEN_HEIGHT - 220, spacing=60)

        # скин будет тут(меню уже есть)





    def draw_settings_menu(self):
        arcade.draw_text("Настройки", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        res_buttons = [(f"{w}x{h}", lambda r=(w, h): self.set_resolution(r)) for w, h in self.resolutions]
        res_buttons.append(("Назад", lambda: setattr(self, 'current_view', 'main')))
        self.draw_buttons(res_buttons, start_y=SCREEN_HEIGHT - 220, spacing=50)

        arcade.draw_text(f"Текущее: {self.resolution[0]}x{self.resolution[1]}",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                         arcade.color.YELLOW, 20, anchor_x="center")

    def draw_buttons(self, button_list, start_y, spacing):
        y = start_y
        for i, (text, _) in enumerate(button_list):
            x = SCREEN_WIDTH // 2
            width = self.button_normal.width
            height = self.button_normal.height
            is_hover = self.hovered_button == i
            tex = self.button_hover if is_hover else self.button_normal
            # Кнопка
            arcade.draw_texture_rect(
                tex,
                rect=arcade.LBWH(
                    x - width // 2,
                    y - height // 2,
                    width,
                    height
                ),
                color=arcade.color.WHITE,
                alpha=255
            )
            arcade.draw_text(text, x, y, arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")
            y -= spacing

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        mapping = {
            "main": 5,
            "levels": 6,
            "skins": 4,
            "settings": len(self.resolutions) + 1
        }
        count = mapping.get(self.current_view, 0)
        self.hovered_button = None
        if count == 0:
            return

        y_start = {
            "main": SCREEN_HEIGHT - 200,
            "levels": SCREEN_HEIGHT - 220,
            "skins": SCREEN_HEIGHT - 220,
            "settings": SCREEN_HEIGHT - 220
        }[self.current_view]
        spacing = 80 if self.current_view == "main" else 60 if self.current_view in ("levels", "skins") else 50

        for i in range(count):
            btn_y = y_start - i * spacing
            if abs(x - SCREEN_WIDTH // 2) < self.button_normal.width // 2 \
               and abs(y - btn_y) < self.button_normal.height // 2:
                self.hovered_button = i
                break

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.hovered_button is None:
            return

        actions = []
        if self.current_view == "main":
            actions = [
                self.start_game,
                lambda: setattr(self, 'current_view', 'levels'),
                lambda: setattr(self, 'current_view', 'skins'),
                lambda: setattr(self, 'current_view', 'settings'),
                arcade.exit
            ]
        elif self.current_view == "levels":
            actions = [lambda lvl=i+1: setattr(self, 'selected_level', lvl) for i in range(5)]
            actions.append(lambda: setattr(self, 'current_view', 'main'))
        elif self.current_view == "skins":
            actions = [lambda s=s: setattr(self, 'selected_skin', s) for s in self.skins]
            actions.append(lambda: setattr(self, 'current_view', 'main'))
        elif self.current_view == "settings":
            actions = [lambda r=r: self.set_resolution(r) for r in self.resolutions]
            actions.append(lambda: setattr(self, 'current_view', 'main'))

        if self.hovered_button < len(actions):
            actions[self.hovered_button]()

    def set_resolution(self, res):
        w, h = res
        self.window.set_size(w, h)
        self.window.center_window()
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = w, h
        self.resolution = (w, h)

    def start_game(self):
        print(f"Запуск: уровень {self.selected_level}, скин {self.selected_skin}")
        arcade.exit()  # временно


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()