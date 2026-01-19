import arcade
import os

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Platformer - Главное меню"

class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        # Загрузка текстур
        path = os.path.join(os.path.dirname(__file__), "assets")
        self.bg = arcade.load_texture(os.path.join(path, "Backgrounds", "blue_grass.png"))
        self.btn_normal = arcade.load_texture(os.path.join(path, "HUD", "hudJewel_red_empty.png"))
        self.btn_hover = arcade.load_texture(os.path.join(path, "HUD", "hudJewel_red.png"))

        # Состояния и данные
        self.state = "menu"
        self.hovered = None
        self.skin = "Beige"
        self.view_skin_now = "Beige"
        self.level = 1
        self.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.options = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        self.skins_list = ["Beige", "Blue", "Green"]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        self.clear()
        # Фон
        arcade.draw_texture_rect(
            self.bg,
            rect=arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            color=arcade.color.WHITE,
            alpha=255
        )
        arcade.draw_text("Platformer", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                         arcade.color.WHITE, 48, anchor_x="center", font_name="Arial")

        # Отрисовка в зависимости от состояния
        if self.state == "menu":
            self.menu_draw()
        elif self.state == "levels":
            self.levels_draw()
        elif self.state == "skins":
            self.skins_draw()
        elif self.state == "settings":
            self.settings_draw()
        elif self.state == "preview":
            self.preview_draw()

    # Главное меню
    def menu_draw(self):
        buttons = [
            ("Играть", self.start_game),
            ("Уровни", lambda: self.change_state("levels")),
            ("Скины", lambda: self.change_state("skins")),
            ("Настройки", lambda: self.change_state("settings")),
            ("Выход", arcade.exit)
        ]
        self.draw_buttons(buttons, SCREEN_HEIGHT - 200, 80)

    # Меню выбора уровня
    def levels_draw(self):
        arcade.draw_text("Выберите уровень", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        btns = [(f"Уровень {i}", lambda x=i: self.set_level(x)) for i in range(1, 6)]
        btns.append(("Назад", lambda: self.change_state("menu")))
        self.draw_buttons(btns, SCREEN_HEIGHT - 220, 60)

    # Меню выбора скина
    def skins_draw(self):
        arcade.draw_text("Выберите героя", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        btns = [(s, lambda x=s: self.show_skin(x)) for s in self.skins_list]
        btns.append(("Назад", lambda: self.change_state("menu")))
        self.draw_buttons(btns, SCREEN_HEIGHT - 220, 60)

    # Открыть предпросмотр скина
    def show_skin(self, name):
        self.view_skin_now = name
        self.state = "preview"

    # Предпросмотр скина
    def preview_draw(self):
        arcade.draw_text(f"Герой: {self.view_skin_now}", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                         arcade.color.WHITE, 36, anchor_x="center")

        path_to_img = os.path.join(os.path.dirname(__file__), "assets", "Players", self.view_skin_now, f"alien{self.view_skin_now}_front.png")
        if os.path.exists(path_to_img):
            img = arcade.load_texture(path_to_img)
            cx = SCREEN_WIDTH // 2
            cy = SCREEN_HEIGHT // 2 + 50
            arcade.draw_texture_rect(
                img,
                rect=arcade.LBWH(
                    cx - min(img.width, 200) // 2,
                    cy - min(img.height, 200) // 2,
                    min(img.width, 200),
                    min(img.height, 200)
                ),
                color=arcade.color.WHITE,
                alpha=255
            )

        btns = [
            ("✅ Выбрать", self.confirm_skin),
            ("← Назад", lambda: self.change_state("skins"))
        ]
        self.draw_buttons(btns, 150, 80)

    # Подтверждение выбора скина
    def confirm_skin(self):
        self.skin = self.view_skin_now
        self.state = "skins"

    # Меню настроек
    def settings_draw(self):
        arcade.draw_text("Настройки", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        btns = [(f"{w}x{h}", lambda res=(w, h): self.set_resolution(res)) for w, h in self.options]
        btns.append(("Назад", lambda: self.change_state("menu")))
        self.draw_buttons(btns, SCREEN_HEIGHT - 220, 50)

        arcade.draw_text(f"Текущее: {self.resolution[0]}x{self.resolution[1]}",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                         arcade.color.YELLOW, 20, anchor_x="center")

    # Отрисовка кнопок
    def draw_buttons(self, btn_list, start_y, spacing):
        y = start_y
        for i, (txt, func) in enumerate(btn_list):
            x = SCREEN_WIDTH // 2
            w = self.btn_normal.width
            h = self.btn_normal.height
            is_hover = self.hovered == i
            btn_tex = self.btn_hover if is_hover else self.btn_normal
            arcade.draw_texture_rect(
                btn_tex,
                rect=arcade.LBWH(x - w // 2, y - h // 2, w, h),
                color=arcade.color.WHITE,
                alpha=255
            )
            arcade.draw_text(txt, x, y, arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")
            y -= spacing

    # Управление состоянием
    def change_state(self, new):
        self.state = new

    def set_level(self, lvl):
        self.level = lvl

    def set_resolution(self, res):
        w, h = res
        self.window.set_size(w, h)
        self.window.center_window()
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = w, h
        self.resolution = res

    def start_game(self):
        from game import GameView
        level_file = "levels/123.tmx"
        game_view = GameView(level_file, self.skin)
        self.window.show_view(game_view)

    # Обработка мыши
    def on_mouse_motion(self, x, y, dx, dy):
        mapping = {
            "menu": 5,
            "levels": 6,
            "skins": 4,
            "settings": len(self.options) + 1,
            "preview": 2
        }
        count = mapping.get(self.state, 0)
        self.hovered = None
        if count == 0:
            return

        start_map = {
            "menu": SCREEN_HEIGHT - 200,
            "levels": SCREEN_HEIGHT - 220,
            "skins": SCREEN_HEIGHT - 220,
            "settings": SCREEN_HEIGHT - 220,
            "preview": 150
        }
        start_y = start_map[self.state]
        sp = 80 if self.state in ("menu", "preview") else 60 if self.state in ("levels", "skins") else 50

        for i in range(count):
            btn_y = start_y - i * sp
            if abs(x - SCREEN_WIDTH // 2) < self.btn_normal.width // 2 and abs(y - btn_y) < self.btn_normal.height // 2:
                self.hovered = i
                break

    def on_mouse_press(self, x, y, btn, mod):
        if self.hovered is None:
            return

        actions_map = {
            "menu": [
                self.start_game,
                lambda: self.change_state("levels"),
                lambda: self.change_state("skins"),
                lambda: self.change_state("settings"),
                arcade.exit
            ],
            "levels": [lambda l=i + 1: self.set_level(l) for i in range(5)] + [lambda: self.change_state("menu")],
            "skins": [lambda s=s: self.show_skin(s) for s in self.skins_list] + [lambda: self.change_state("menu")],
            "settings": [lambda r=r: self.set_resolution(r) for r in self.options] + [lambda: self.change_state("menu")],
            "preview": [
                self.confirm_skin,
                lambda: self.change_state("skins")
            ]
        }

        actions = actions_map.get(self.state, [])
        if self.hovered < len(actions):
            actions[self.hovered]()


def main():
    win = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu = Menu()
    win.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()