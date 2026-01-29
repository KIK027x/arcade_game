import arcade
import os

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Across the Worlds - Главное меню"

SKIN_NAMES = {
    "p1": "Зелёный",
    "p2": "Синий",
    "p3": "Розовый"
}

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
        self.selected_level = 1
        self.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.options = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]

        # Настройки
        from database import get_volume, get_player_data
        data = get_player_data()
        self.settings_volume = data["volume"]
        self.settings_death_enabled = data["death_screen_enabled"]
        self.settings_state = "main"

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
        arcade.draw_text("Across the Worlds", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                         arcade.color.GRAY, 48, anchor_x="center", font_name="Arial")

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
                         arcade.color.GRAY, 36, anchor_x="center")
        btns = [(f"Уровень {i}", lambda x=i: self.select_level(x)) for i in range(1, 4)]
        btns.append(("Назад", lambda: self.change_state("menu")))
        self.draw_buttons(btns, SCREEN_HEIGHT - 220, 60)

    def skins_draw(self):
        arcade.draw_text("Выберите героя", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.GRAY, 36, anchor_x="center")
        btns = []
        for s in self.skins_list:
            display_name = SKIN_NAMES[s["name"]] if s["unlocked"] else f"{SKIN_NAMES[s['name']]} ({s['price']} монет)"
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

        arcade.draw_text(f"Герой: {SKIN_NAMES[self.view_skin_now]}", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                         arcade.color.GRAY, 36, anchor_x="center")

        path_to_img = os.path.join(
            os.path.dirname(__file__),
            "assets", "Player",
            f"{self.view_skin_now}_front.png"
        )
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
            # === Цвет текста ===
            if txt.startswith(("✅", "💰", "←")):
                text_color = arcade.color.GRAY
            else:
                text_color = arcade.color.GRAY
            arcade.draw_text(txt, x, y, text_color, 18, anchor_x="center", anchor_y="center")
            y -= spacing

    def settings_draw(self):
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        # === Заголовок "Настройки" ВЫШЕ ===
        arcade.draw_text("Настройки", w // 2, h - 150, arcade.color.GRAY, 48, anchor_x="center")

        if self.settings_state == "main":
            buttons = [
                ("🖥️ Разрешение", lambda: setattr(self, 'settings_state', 'resolution')),
                ("🔊 Звук", lambda: setattr(self, 'settings_state', 'sound')),
                ("🎮 Игра", lambda: setattr(self, 'settings_state', 'game')),
                ("← Назад", lambda: setattr(self, 'state', 'menu'))
            ]
            y = h - 250  # === Ниже заголовка ===
            for i, (text, _) in enumerate(buttons):
                color = arcade.color.YELLOW if self.hovered == i else arcade.color.GRAY
                arcade.draw_text(text, w // 2, y, color, 24, anchor_x="center")
                y -= 50

        elif self.settings_state == "resolution":
            # === Заголовок "Разрешение" ВЫШЕ ===
            arcade.draw_text("Разрешение", w // 2, h - 200, arcade.color.GRAY, 48, anchor_x="center")
            y = h - 250  # === Ниже заголовка ===
            for i, (res_w, res_h) in enumerate(self.options):
                text = f"{res_w}x{res_h}"
                color = arcade.color.YELLOW if (res_w, res_h) == (w, h) else arcade.color.GRAY
                arcade.draw_text(text, w // 2, y, color, 24, anchor_x="center")
                y -= 50
            arcade.draw_text("← Назад", w // 2, 50, arcade.color.GRAY, 24, anchor_x="center")

        elif self.settings_state == "sound":
            # === Заголовок "Звук" ВЫШЕ ===
            arcade.draw_text("Звук", w // 2, h - 200, arcade.color.GRAY, 48, anchor_x="center")
            slider_x, slider_y = w // 2, h // 2
            slider_width = 300
            slider_height = 20
            handle_radius = 10

            arcade.draw_lrbt_rectangle_filled(
                slider_x - slider_width // 2,
                slider_x + slider_width // 2,
                slider_y - slider_height // 2,
                slider_y + slider_height // 2,
                arcade.color.GRAY
            )

            fill_width = int(slider_width * self.settings_volume)
            arcade.draw_lrbt_rectangle_filled(
                slider_x - slider_width // 2,
                slider_x - slider_width // 2 + fill_width,
                slider_y - slider_height // 2,
                slider_y + slider_height // 2,
                arcade.color.GREEN
            )

            handle_x = slider_x - slider_width // 2 + fill_width
            arcade.draw_circle_filled(handle_x, slider_y, handle_radius, arcade.color.WHITE)

            arcade.draw_text(f"Громкость: {int(self.settings_volume * 100)}%", w // 2, h // 2 + 50, arcade.color.GRAY, 24, anchor_x="center")
            arcade.draw_text("← Назад", w // 2, 50, arcade.color.GRAY, 24, anchor_x="center")

        elif self.settings_state == "game":
            # === Заголовок "Игра" ВЫШЕ ===
            arcade.draw_text("Игра", w // 2, h - 200, arcade.color.GRAY, 48, anchor_x="center")
            status = "Вкл" if self.settings_death_enabled else "Выкл"
            arcade.draw_text(f"Экран смерти: {status}", w // 2, h // 2, arcade.color.GRAY, 24, anchor_x="center")
            arcade.draw_text("← Назад", w // 2, 50, arcade.color.GRAY, 24, anchor_x="center")

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
            # === Цвет текста ===
            if txt.startswith(("▶", "⚙", "🚪", "←", "🖥️", "🔊", "🎮")):
                text_color = arcade.color.GRAY
            else:
                text_color = arcade.color.GRAY
            arcade.draw_text(txt, x, y, text_color, 18, anchor_x="center", anchor_y="center")
            y -= spacing

    def change_state(self, new):
        self.state = new

    def select_level(self, lvl):
        self.selected_level = lvl

    def set_resolution(self, res):
        w, h = res
        self.window.set_size(w, h)
        self.window.center_window()
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = w, h
        self.resolution = res

    def start_game(self):
        from game import GameView
        level_file = f"levels/level{self.selected_level}.tmx"
        game_view = GameView(level_file, self.skin)
        self.window.show_view(game_view)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.state == "preview":
            self.hovered = None
            y_start = 150
            spacing = 80
            for i in range(len(self.preview_buttons)):
                btn_y = y_start - i * spacing
                if abs(x - SCREEN_WIDTH // 2) < self.btn_normal.width // 2 and abs(y - btn_y) < self.btn_normal.height // 2:
                    self.hovered = i
                    break
            return

        if self.state == "settings":
            w, h = SCREEN_WIDTH, SCREEN_HEIGHT
            self.hovered = None
            if self.settings_state == "main":
                for i in range(4):
                    btn_y = h - 300 - i * 50  # === Сдвинуто ещё ниже ===
                    if abs(x - w // 2) < 150 and abs(y - btn_y) < 20:
                        self.hovered = i
                        return
            elif self.settings_state == "resolution":
                if abs(x - w // 2) < 150 and abs(y - 50) < 20:
                    self.hovered = "back"
            elif self.settings_state == "sound":
                if abs(x - w // 2) < 150 and abs(y - 50) < 20:
                    self.hovered = "back"
                # Проверка на ползунок
                slider_x = w // 2
                slider_y = h // 2
                if abs(y - slider_y) < 15 and abs(x - (slider_x - 150)) <= 300:
                    self.hovered = "slider"
            elif self.settings_state == "game":
                if abs(x - w // 2) < 150 and abs(y - 50) < 20:
                    self.hovered = "back"
            return

        mapping = {
            "menu": 5,
            "levels": 4,
            "skins": len(self.skins_list) + 1,
        }
        count = mapping.get(self.state, 0)
        self.hovered = None
        if count == 0:
            return

        start_map = {
            "menu": SCREEN_HEIGHT - 200,
            "levels": SCREEN_HEIGHT - 220,
            "skins": SCREEN_HEIGHT - 220,
        }
        start_y = start_map[self.state]
        sp = 80 if self.state == "menu" else 60

        for i in range(count):
            btn_y = start_y - i * sp
            if abs(x - SCREEN_WIDTH // 2) < self.btn_normal.width // 2 and abs(y - btn_y) < self.btn_normal.height // 2:
                self.hovered = i
                break

    def on_mouse_press(self, x, y, btn, mod):
        if self.hovered is None:
            return

        if self.state == "preview":
            if self.hovered < len(self.preview_buttons):
                self.preview_buttons[self.hovered][1]()
            return

        if self.state == "settings":
            w, h = SCREEN_WIDTH, SCREEN_HEIGHT
            if self.settings_state == "main":
                if self.hovered is not None and self.hovered < 4:
                    actions = [
                        lambda: setattr(self, 'settings_state', 'resolution'),
                        lambda: setattr(self, 'settings_state', 'sound'),
                        lambda: setattr(self, 'settings_state', 'game'),
                        lambda: setattr(self, 'state', 'menu')
                    ]
                    actions[self.hovered]()
            elif self.settings_state == "resolution":
                if self.hovered == "back":
                    self.settings_state = "main"
                else:
                    for i, (res_w, res_h) in enumerate(self.options):
                        btn_y = h - 300 - i * 50  # === Сдвинуто ещё ниже ===
                        if abs(x - w // 2) < 150 and abs(y - btn_y) < 20:
                            self.set_resolution((res_w, res_h))
                            return
            elif self.settings_state == "sound":
                if self.hovered == "back":
                    self.settings_state = "main"
                else:
                    # Обработка ползунка
                    slider_x = SCREEN_WIDTH // 2
                    if abs(y - SCREEN_HEIGHT // 2) < 30 and (slider_x - 150 <= x <= slider_x + 150):
                        rel_x = max(0, min(300, x - (slider_x - 150)))
                        self.settings_volume = rel_x / 300
                        from database import set_volume
                        set_volume(self.settings_volume)
            elif self.settings_state == "game":
                if self.hovered == "back":
                    self.settings_state = "main"
                else:
                    if abs(x - w // 2) < 200 and abs(y - h // 2) < 20:
                        self.settings_death_enabled = not self.settings_death_enabled
                        from database import set_death_screen
                        set_death_screen(self.settings_death_enabled)
            return

        actions_map = {
            "menu": [
                self.start_game,
                lambda: self.change_state("levels"),
                lambda: self.change_state("skins"),
                lambda: self.change_state("settings"),
                arcade.exit
            ],
            "levels": [lambda l=i + 1: self.select_level(l) for i in range(3)] + [lambda: self.change_state("menu")],
            "skins": [self.make_skin_handler(s["name"]) for s in self.skins_list] + [lambda: self.change_state("menu")],
        }

        actions = actions_map.get(self.state, [])
        if self.hovered < len(actions) and actions[self.hovered]:
            actions[self.hovered]()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.state == "settings" and self.settings_state == "sound":
            w = SCREEN_WIDTH
            slider_x = w // 2
            if abs(y - SCREEN_HEIGHT // 2) < 30 and (slider_x - 150 <= x <= slider_x + 150):
                rel_x = max(0, min(300, x - (slider_x - 150)))
                self.settings_volume = rel_x / 300
                from database import set_volume
                set_volume(self.settings_volume)


def main():
    win = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu = Menu()
    win.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()