import arcade
import os

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Platformer - Главное меню"

class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        from database import init_db, get_player_data, get_skins
        init_db()
        data = get_player_data()
        self.skin = data["active_skin"]
        self.view_skin_now = self.skin
        self.skins_list = get_skins()
        self.coins = data["coins"]

        path = os.path.join(os.path.dirname(__file__), "assets")
        self.bg = arcade.load_texture(os.path.join(path, "Backgrounds", "blue_grass.png"))
        self.btn_normal = arcade.load_texture(os.path.join(path, "HUD", "hudJewel_red_empty.png"))
        self.btn_hover = arcade.load_texture(os.path.join(path, "HUD", "hudJewel_red.png"))

        self.state = "menu"
        self.hovered = None
        self.level = 1
        self.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.options = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)
        from database import get_player_data, get_skins
        data = get_player_data()
        self.coins = data["coins"]
        self.skins_list = get_skins()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.bg,
            rect=arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            color=arcade.color.WHITE,
            alpha=255
        )
        arcade.draw_text(f"Монеты: {self.coins}", 20, SCREEN_HEIGHT - 40, arcade.color.YELLOW, 24)
        arcade.draw_text("Platformer", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                         arcade.color.WHITE, 48, anchor_x="center", font_name="Arial")

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

    def menu_draw(self):
        buttons = [
            ("Играть", self.start_game),
            ("Уровни", lambda: self.change_state("levels")),
            ("Скины", lambda: self.change_state("skins")),
            ("Настройки", lambda: self.change_state("settings")),
            ("Выход", arcade.exit)
        ]
        self.draw_buttons(buttons, SCREEN_HEIGHT - 200, 80)

    def levels_draw(self):
        arcade.draw_text("Выберите уровень", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        btns = [(f"Уровень {i}", lambda x=i: self.set_level(x)) for i in range(1, 6)]
        btns.append(("Назад", lambda: self.change_state("menu")))
        self.draw_buttons(btns, SCREEN_HEIGHT - 220, 60)

    def skins_draw(self):
        arcade.draw_text("Выберите героя", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        btns = []
        for s in self.skins_list:
            display_name = s["name"] if s["unlocked"] else f"{s['name']} ({s['price']} монет)"
            btns.append((display_name, self.make_skin_handler(s["name"])))
        btns.append(("Назад", lambda: self.change_state("menu")))
        self.draw_buttons(btns, SCREEN_HEIGHT - 220, 60)

    def make_skin_handler(self, skin_name):
        def handler():
            self.view_skin_now = skin_name
            self.state = "preview"
        return handler

    def preview_draw(self):
        from database import get_skins, get_coins
        skins = {s["name"]: s for s in get_skins()}
        current = skins[self.view_skin_now]
        self.coins = get_coins()

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

        # Кнопки в предпросмотре
        self.preview_buttons = []
        y_start = 150
        spacing = 80

        if current["unlocked"]:
            def select_handler():
                from database import set_active_skin
                set_active_skin(self.view_skin_now)
                self.skin = self.view_skin_now
            self.preview_buttons.append(("✅ Выбрать", select_handler))
        else:
            if self.coins >= current["price"]:
                def buy_handler():
                    from database import buy_skin
                    if buy_skin(self.view_skin_now):
                        from database import get_skins, get_player_data
                        self.skins_list = get_skins()
                        self.coins = get_player_data()["coins"]
                self.preview_buttons.append(("💰 Купить за 50 монет", buy_handler))
            else:
                self.preview_buttons.append((f"Нужно {current['price']} монет", lambda: None))

        self.preview_buttons.append(("← Назад", lambda: self.change_state("skins")))

        # Отрисовка кнопок
        y = y_start
        for i, (txt, func) in enumerate(self.preview_buttons):
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

    def settings_draw(self):
        arcade.draw_text("Настройки", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.WHITE, 36, anchor_x="center")
        btns = [(f"{w}x{h}", lambda res=(w, h): self.set_resolution(res)) for w, h in self.options]
        btns.append(("Назад", lambda: self.change_state("menu")))
        self.draw_buttons(btns, SCREEN_HEIGHT - 220, 50)

        arcade.draw_text(f"Текущее: {self.resolution[0]}x{self.resolution[1]}",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                         arcade.color.YELLOW, 20, anchor_x="center")

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

    def on_mouse_motion(self, x, y, dx, dy):
        if self.state == "preview":
            # Обработка наведения в preview
            self.hovered = None
            y_start = 150
            spacing = 80
            for i in range(len(self.preview_buttons)):
                btn_y = y_start - i * spacing
                if abs(x - SCREEN_WIDTH // 2) < self.btn_normal.width // 2 and abs(y - btn_y) < self.btn_normal.height // 2:
                    self.hovered = i
                    break
            return

        mapping = {
            "menu": 5,
            "levels": 6,
            "skins": len(self.skins_list) + 1,
            "settings": len(self.options) + 1,
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
        }
        start_y = start_map[self.state]
        sp = 80 if self.state == "menu" else 60 if self.state in ("levels", "skins") else 50

        for i in range(count):
            btn_y = start_y - i * sp
            if abs(x - SCREEN_WIDTH // 2) < self.btn_normal.width // 2 and abs(y - btn_y) < self.btn_normal.height // 2:
                self.hovered = i
                break

    def on_mouse_press(self, x, y, btn, mod):
        if self.hovered is None:
            return

        if self.state == "preview":
            # Обработка клика в preview
            if self.hovered < len(self.preview_buttons):
                self.preview_buttons[self.hovered][1]()
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
            "skins": [self.make_skin_handler(s["name"]) for s in self.skins_list] + [lambda: self.change_state("menu")],
            "settings": [lambda r=r: self.set_resolution(r) for r in self.options] + [lambda: self.change_state("menu")],
        }

        actions = actions_map.get(self.state, [])
        if self.hovered < len(actions) and actions[self.hovered]:
            actions[self.hovered]()


def main():
    win = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu = Menu()
    win.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()
