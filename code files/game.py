import arcade
import os
import time
import sys
from level import Level
from PIL import Image, ImageOps
from io import BytesIO
import pyglet
import re

# === НОВАЯ ФУНКЦИЯ resource_path ===
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

DUCK_OFFSET = 20

# === ВСЕ ВРАГИ ===
class Spinner(arcade.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.start_x = x
        self.move_direction = 1
        self.speed = 2.0
        self.animation_timer = 0
        self.is_spinning = False

        path = resource_path(os.path.join("assets", "Enemies"))
        self.idle_texture = arcade.load_texture(os.path.join(path, "spinner.png"))
        self.spin_texture = arcade.load_texture(os.path.join(path, "spinner_spin.png"))

        self.texture = self.idle_texture

    def update(self, delta_time):
        self.center_x += self.speed * self.move_direction
        if abs(self.center_x - self.start_x) >= 128:
            self.move_direction *= -1

        self.animation_timer += delta_time
        if self.animation_timer > 0.1:
            self.is_spinning = not self.is_spinning
            self.texture = self.spin_texture if self.is_spinning else self.idle_texture
            self.animation_timer = 0


class Branacle(arcade.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.animation_timer = 0
        self.is_biting = False
        self.animation_speed = 2.0

        path = resource_path(os.path.join("assets", "Enemies"))
        self.idle_texture = arcade.load_texture(os.path.join(path, "barnacle.png"))
        self.bite_texture = arcade.load_texture(os.path.join(path, "barnacle_bite.png"))

        self.texture = self.idle_texture

    def update(self, delta_time):
        self.animation_timer += delta_time
        if self.animation_timer > 1.0 / self.animation_speed:
            self.is_biting = not self.is_biting
            self.texture = self.bite_texture if self.is_biting else self.idle_texture
            self.animation_timer = 0


class SlimeGreen(arcade.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.animation_timer = 0
        self.walk_frame = 0
        self.direction = -1
        self.speed = 70
        self.radius = 140
        self.start_x = x
        self.is_jumping = False
        self.jump_timer = 0
        self.jump_duration = 0.5
        self.jumping_height = 70
        self.original_y = y
        self.jump_cooldown = 0
        self.jump_interval = 1.5

        self.current_jumps = 0
        self.target_jumps = 2
        self.moving_left_first = True
        self.min_x = x - self.radius
        self.max_x = x + self.radius
        self.target_x = x

        path = resource_path(os.path.join("assets", "Enemies"))
        self.idle_texture = arcade.load_texture(os.path.join(path, "slimeGreen.png"))
        self.idle_texture_flipped = self._load_flipped_texture(os.path.join(path, "slimeGreen.png"))
        self.walk_texture = arcade.load_texture(os.path.join(path, "slimeGreen_walk.png"))
        self.walk_texture_flipped = self._load_flipped_texture(os.path.join(path, "slimeGreen_walk.png"))
        self.squash_texture = arcade.load_texture(os.path.join(path, "slimeGreen_squashed.png"))
        self.squash_texture_flipped = self._load_flipped_texture(os.path.join(path, "slimeGreen_squashed.png"))

        self.texture = self.idle_texture
        self.is_dead = False
        self.death_timer = 0

    def _load_flipped_texture(self, image_path):
        image = Image.open(image_path).convert("RGBA")
        flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
        byte_arr = BytesIO()
        flipped_image.save(byte_arr, format='PNG')
        return arcade.load_texture(BytesIO(byte_arr.getvalue()))

    def update(self, delta_time, physics_engine):
        if self.is_dead:
            self.death_timer += delta_time
            if self.death_timer > 1.0:
                self.remove_from_sprite_lists()
            else:
                alpha = int(255 * (1.0 - self.death_timer))
                self.alpha = alpha
            return

        self.jump_cooldown += delta_time
        if not self.is_jumping and self.jump_cooldown >= self.jump_interval:
            self.is_jumping = True
            self.jump_timer = 0
            self.jump_cooldown = 0
            self.current_jumps += 1

            if self.current_jumps >= self.target_jumps:
                self.direction *= -1
                self.current_jumps = 0

                if self.moving_left_first:
                    self.target_jumps = 4
                    self.moving_left_first = False
                else:
                    pass

            proposed_x = self.center_x + self.speed * self.direction
            if self.min_x <= proposed_x <= self.max_x:
                self.target_x = proposed_x

        if self.is_jumping:
            self.jump_timer += delta_time
            progress = self.jump_timer / self.jump_duration
            if progress < 1:
                self.center_y = self.original_y + self.jumping_height * (1 - (progress - 0.5)**2 * 4)
                self.center_x = self.center_x + (self.target_x - self.center_x) * delta_time * 2
            else:
                self.center_y = self.original_y
                self.is_jumping = False
                self.jump_timer = 0

        self.animation_timer += delta_time
        if self.animation_timer > 0.2:
            self.animation_timer = 0

        if self.direction == -1:
            if self.is_jumping:
                self.texture = self.walk_texture
            else:
                self.texture = self.idle_texture
        else:
            if self.is_jumping:
                self.texture = self.walk_texture_flipped
            else:
                self.texture = self.idle_texture_flipped

    def squash(self, game_view):
        if self.direction == -1:
            self.texture = self.squash_texture
        else:
            self.texture = self.squash_texture_flipped
        self.is_dead = True
        self.death_timer = 0
        self.alpha = 255

        import random
        coins_to_add = random.randint(10, 15)
        game_view.collected_coins += coins_to_add
        from database import get_volume
        current_volume = get_volume()
        game_view.coin_sound.play(volume=current_volume)


class Player(arcade.Sprite):
    def __init__(self, skin_name):
        super().__init__()
        self.skin_name = skin_name
        path = resource_path(os.path.join("assets", "Player"))

        idle_path = os.path.join(path, f"{skin_name}_stand.png")
        self.idle_texture = arcade.load_texture(idle_path)
        self.idle_texture_flipped = self._load_flipped_texture(idle_path)

        jump_path = os.path.join(path, f"{skin_name}_jump.png")
        self.jump_texture = arcade.load_texture(jump_path)
        self.jump_texture_flipped = self._load_flipped_texture(jump_path)

        duck_path = os.path.join(path, f"{skin_name}_duck.png")
        self.duck_texture = self._create_offset_texture(duck_path, DUCK_OFFSET)
        self.duck_texture_flipped = self._create_offset_texture_flipped(duck_path, DUCK_OFFSET)

        walk_path = os.path.join(path, f"{skin_name}_walk", "PNG")
        self.walk_frames = []
        self.walk_frames_flipped = []
        for i in range(1, 12):
            filename = f"{skin_name}_walk{i:02d}.png"
            filepath = os.path.join(walk_path, filename)
            if os.path.exists(filepath):
                texture = arcade.load_texture(filepath)
                texture_flipped = self._load_flipped_texture(filepath)
                self.walk_frames.append(texture)
                self.walk_frames_flipped.append(texture_flipped)

        if not self.walk_frames:
            self.walk_frames = [self.idle_texture]
            self.walk_frames_flipped = [self.idle_texture_flipped]

        self.texture = self.idle_texture
        self.base_speed_x = 5
        self.base_jump_y = 12
        self.walk_frame = 0
        self.walk_timer = 0
        self.direction = 1
        self.is_ducking = False

    def _load_flipped_texture(self, image_path):
        image = Image.open(image_path).convert("RGBA")
        flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
        byte_arr = BytesIO()
        flipped_image.save(byte_arr, format='PNG')
        return arcade.load_texture(BytesIO(byte_arr.getvalue()))

    def _create_offset_texture(self, image_path, offset_y):
        image = Image.open(image_path).convert("RGBA")
        w, h = image.size
        new_image = Image.new("RGBA", (w, h + offset_y), (0, 0, 0, 0))
        new_image.paste(image, (0, offset_y))
        byte_arr = BytesIO()
        new_image.save(byte_arr, format='PNG')
        return arcade.load_texture(BytesIO(byte_arr.getvalue()))

    def _create_offset_texture_flipped(self, image_path, offset_y):
        image = Image.open(image_path).convert("RGBA")
        flipped = image.transpose(Image.FLIP_LEFT_RIGHT)
        w, h = flipped.size
        new_image = Image.new("RGBA", (w, h + offset_y), (0, 0, 0, 0))
        new_image.paste(flipped, (0, offset_y))
        byte_arr = BytesIO()
        new_image.save(byte_arr, format='PNG')
        return arcade.load_texture(BytesIO(byte_arr.getvalue()))

    def set_initial_position(self, x, y):
        self.center_x = x
        self.center_y = y

    def update_animation(self, delta_time, physics_engine, is_ducking):
        self.walk_timer += delta_time
        self.is_ducking = is_ducking

        if self.change_x < 0:
            self.direction = -1
        elif self.change_x > 0:
            self.direction = 1

        if is_ducking:
            if self.direction == -1:
                self.texture = self.duck_texture_flipped
            else:
                self.texture = self.duck_texture
        else:
            if not physics_engine.can_jump():
                if self.direction == -1:
                    self.texture = self.jump_texture_flipped
                else:
                    self.texture = self.jump_texture
            elif abs(self.change_x) > 0:
                if self.walk_timer > 0.1:
                    self.walk_frame = (self.walk_frame + 1) % len(self.walk_frames)
                    self.walk_timer = 0
                if self.direction == -1:
                    self.texture = self.walk_frames_flipped[self.walk_frame]
                else:
                    self.texture = self.walk_frames[self.walk_frame]
            else:
                if self.direction == -1:
                    self.texture = self.idle_texture_flipped
                else:
                    self.texture = self.idle_texture


class SpinnerHalf(arcade.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.animation_timer = 0
        self.is_spinning = False

        path = resource_path(os.path.join("assets", "Enemies"))
        self.idle_texture = arcade.load_texture(os.path.join(path, "spinnerHalf.png"))
        self.spin_texture = arcade.load_texture(os.path.join(path, "spinnerHalf_spin.png"))

        self.texture = self.idle_texture

    def update(self, delta_time):
        self.animation_timer += delta_time
        if self.animation_timer > 0.1:
            self.is_spinning = not self.is_spinning
            self.texture = self.spin_texture if self.is_spinning else self.idle_texture
            self.animation_timer = 0


# === ЭКРАНЫ ===
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
        arcade.draw_text("🚪 Выйти в меню", w // 2, h - 400, arcade.color.WHITE, 24, anchor_x="center")

    def on_mouse_press(self, x, y):
        w, h = self.game_view.window.width, self.game_view.window.height
        if abs(x - w // 2) < 150 and abs(y - (h - 350)) < 20:
            self.game_view.restart_level()
        elif abs(x - w // 2) < 150 and abs(y - (h - 400)) < 20:
            if self.game_view.level_music_player:
                self.game_view.level_music_player.pause()
            from main_menu import Menu
            menu = Menu()
            self.game_view.window.show_view(menu)

    def on_mouse_motion(self, x, y, dx, dy):
        pass


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
            if self.game_view.level_music_player:
                self.game_view.level_music_player.pause()
            from main_menu import Menu
            menu = Menu()
            self.game_view.window.show_view(menu)

    def on_mouse_motion(self, x, y, dx, dy):
        pass


# === НАСТРОЙКИ ===
class SettingsMenu:
    def __init__(self, parent_view):
        self.parent_view = parent_view
        self.current_tab = "main"
        self.hovered = None
        self.dragging_slider = False
        self.options = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]

        from database import get_player_data, get_volume
        data = get_player_data()
        self.death_enabled = data["death_screen_enabled"]
        self.volume = get_volume()

    def draw(self):
        w, h = self.parent_view.window.width, self.parent_view.window.height
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (0, 0, 0, 180))

        if self.current_tab == "main":
            arcade.draw_text("Настройки", w // 2, h - 150, arcade.color.WHITE, 48, anchor_x="center")
            buttons = [
                ("🖥️ Разрешение", lambda: setattr(self, 'current_tab', 'resolution')),
                ("🔊 Звук", lambda: setattr(self, 'current_tab', 'sound')),
                ("🎮 Игра", lambda: setattr(self, 'current_tab', 'game')),
                ("← Назад", self.go_back)
            ]
            y = h - 250
            for i, (text, _) in enumerate(buttons):
                color = arcade.color.YELLOW if self.hovered == i else arcade.color.WHITE
                arcade.draw_text(text, w // 2, y, color, 24, anchor_x="center")
                y -= 50

        elif self.current_tab == "resolution":
            arcade.draw_text("Разрешение", w // 2, h - 150, arcade.color.WHITE, 48, anchor_x="center")
            y = h - 250
            for i, (res_w, res_h) in enumerate(self.options):
                text = f"{res_w}x{res_h}"
                color = arcade.color.YELLOW if (res_w, res_h) == (w, h) else arcade.color.WHITE
                arcade.draw_text(text, w // 2, y, color, 24, anchor_x="center")
                y -= 50
            arcade.draw_text("← Назад", w // 2, 50, arcade.color.WHITE, 24, anchor_x="center")

        elif self.current_tab == "sound":
            arcade.draw_text("Звук", w // 2, h - 150, arcade.color.WHITE, 48, anchor_x="center")
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

            fill_width = int(slider_width * self.volume)
            arcade.draw_lrbt_rectangle_filled(
                slider_x - slider_width // 2,
                slider_x - slider_width // 2 + fill_width,
                slider_y - slider_height // 2,
                slider_y + slider_height // 2,
                arcade.color.GREEN
            )

            handle_x = slider_x - slider_width // 2 + fill_width
            arcade.draw_circle_filled(handle_x, slider_y, handle_radius, arcade.color.WHITE)

            arcade.draw_text(f"Громкость: {int(self.volume * 100)}%", w // 2, h // 2 + 50, arcade.color.WHITE, 24, anchor_x="center")
            arcade.draw_text("← Назад", w // 2, 50, arcade.color.WHITE, 24, anchor_x="center")

        elif self.current_tab == "game":
            arcade.draw_text("Игра", w // 2, h - 150, arcade.color.WHITE, 48, anchor_x="center")
            status = "Вкл" if self.death_enabled else "Выкл"
            arcade.draw_text(f"Экран смерти: {status}", w // 2, h // 2, arcade.color.WHITE, 24, anchor_x="center")
            arcade.draw_text("← Назад", w // 2, 50, arcade.color.WHITE, 24, anchor_x="center")

    def go_back(self):
        if self.current_tab == "main":
            self.parent_view.pause_menu.in_settings = False
        else:
            self.current_tab = "main"

    def on_mouse_motion(self, x, y):
        w, h = self.parent_view.window.width, self.parent_view.window.height
        self.hovered = None

        if self.current_tab == "main":
            for i in range(4):
                btn_y = h - 250 - i * 50
                if abs(x - w // 2) < 150 and abs(y - btn_y) < 20:
                    self.hovered = i
                    return
        elif self.current_tab == "resolution":
            if abs(x - w // 2) < 150 and abs(y - 50) < 20:
                self.hovered = "back"
        elif self.current_tab == "sound":
            if abs(x - w // 2) < 150 and abs(y - 50) < 20:
                self.hovered = "back"
            slider_x = w // 2
            slider_y = h // 2
            if abs(y - slider_y) < 15:
                self.dragging_slider = True
        elif self.current_tab == "game":
            if abs(x - w // 2) < 150 and abs(y - 50) < 20:
                self.hovered = "back"

    def on_mouse_press(self, x, y):
        w, h = self.parent_view.window.width, self.parent_view.window.height

        if self.current_tab == "main":
            if self.hovered is not None and self.hovered < 4:
                actions = [
                    lambda: setattr(self, 'current_tab', 'resolution'),
                    lambda: setattr(self, 'current_tab', 'sound'),
                    lambda: setattr(self, 'current_tab', 'game'),
                    self.go_back
                ]
                actions[self.hovered]()

        elif self.current_tab == "resolution":
            if self.hovered == "back":
                self.current_tab = "main"
            else:
                for i, (res_w, res_h) in enumerate(self.options):
                    btn_y = h - 250 - i * 50
                    if abs(x - w // 2) < 150 and abs(y - btn_y) < 20:
                        self.parent_view.window.set_size(res_w, res_h)
                        self.parent_view.window.center_window()
                        return

        elif self.current_tab == "sound":
            if self.hovered == "back":
                self.current_tab = "main"
            else:
                slider_x = w // 2
                if abs(y - h // 2) < 15:
                    rel_x = max(0, min(300, x - (slider_x - 150)))
                    self.volume = rel_x / 300
                    from database import set_volume
                    set_volume(self.volume)

        elif self.current_tab == "game":
            if self.hovered == "back":
                self.current_tab = "main"
            else:
                if abs(x - w // 2) < 200 and abs(y - h // 2) < 20:
                    self.death_enabled = not self.death_enabled
                    from database import set_death_screen
                    set_death_screen(self.death_enabled)

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging_slider = False


# === ПАУЗА ===
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

    def on_mouse_release(self, x, y, button, modifiers):
        if self.in_settings:
            self.settings_menu.on_mouse_release(x, y, button, modifiers)

    def resume(self):
        self.game_view.paused = False

    def settings(self):
        self.in_settings = True
        self.settings_menu = SettingsMenu(self.game_view)

    def go_to_main_menu(self):
        if self.game_view.level_music_player:
            self.game_view.level_music_player.pause()
        from main_menu import Menu
        menu = Menu()
        self.game_view.window.show_view(menu)


# === ИГРОВОЙ ПРОЦЕСС ===
class GameView(arcade.View):
    def __init__(self, level_path, skin):
        super().__init__()
        # === ИСПОЛЬЗУЕМ resource_path для уровня ===
        self.level_path = resource_path(level_path)
        self.skin = skin
        self.start_time = time.time()

        # --- Камеры ---
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.camera_shake = arcade.camera.grips.ScreenShake2D(
            self.world_camera.view_data,
            max_amplitude=5.0,
            acceleration_duration=0.1,
            falloff_time=0.3,
            shake_frequency=8.0,
        )

        # Определяем имя музыки: lv1.mp3, lv2.mp3, lv3.mp3
        self.music_file = self._get_music_filename(self.level_path)

        self.setup()
        self.window.set_mouse_visible(True)

    def _get_music_filename(self, path: str) -> str:
        match = re.search(r'level(\d+)', path, re.IGNORECASE)
        num = match.group(1) if match else "1"
        return f"lv{num}.mp3"

    def setup(self):
        self.level = Level(self.level_path)
        self.player_sprite = Player(self.skin)
        self.player_sprite.set_initial_position(
            self.window.width // 2,
            self.window.height // 2
        )

        # Делаем KeyBlock частью платформ → непроходимым!
        all_platforms = arcade.SpriteList()
        all_platforms.extend(self.level.platforms)
        all_platforms.extend(self.level.key_blocks)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=all_platforms,
            gravity_constant=0.5
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.spinner_list = arcade.SpriteList()
        for spinner in self.level.spinners:
            new_spinner = Spinner(spinner.center_x, spinner.center_y, spinner.scale)
            self.spinner_list.append(new_spinner)

        self.collected_coins = 0
        self.has_key = False
        self.paused = False
        self.pause_menu = PauseMenu(self)
        self.death_screen = None
        self.win_screen = None
        self.is_ducking = False
        self.game_active = True

        self.spinner_half_list = arcade.SpriteList()
        for spinner in self.level.spinner_half:
            new_spinner = SpinnerHalf(spinner.center_x, spinner.center_y, spinner.scale)
            self.spinner_half_list.append(new_spinner)

        # === Branacle ===
        self.branacle_list = arcade.SpriteList()
        for br in self.level.branacles:
            new_br = Branacle(br.center_x, br.center_y, br.scale)
            self.branacle_list.append(new_br)

        # === Slime Green ===
        self.slime_green_list = arcade.SpriteList()
        for sl in self.level.slimes_green:
            new_sl = SlimeGreen(sl.center_x, sl.center_y, sl.scale)
            self.slime_green_list.append(new_sl)

        # === ЗВУКИ ===
        sounds_path = resource_path("Sounds")
        self.coin_sound = arcade.Sound(os.path.join(sounds_path, "Coin.mp3"))
        self.jump_sound = arcade.Sound(os.path.join(sounds_path, "Jump.mp3"))
        self.key_sound = arcade.Sound(os.path.join(sounds_path, "Key.mp3"))
        self.death_sound = arcade.Sound(os.path.join(sounds_path, "Death.mp3"))

        # === ЗВУК ПИЛЫ ===
        spinner_source = pyglet.media.load(os.path.join(sounds_path, "Spinner.mp3"), streaming=False)
        self.spinner_player = pyglet.media.Player()
        self.spinner_player.queue(spinner_source)
        self.spinner_player.loop = True
        self.spinner_player.volume = 0.0

        # === ФОНОВАЯ МУЗЫКА УРОВНЯ ===
        music_path = os.path.join(sounds_path, self.music_file)
        if os.path.exists(music_path):
            music_source = pyglet.media.load(music_path, streaming=True)
            self.level_music_player = pyglet.media.Player()
            self.level_music_player.queue(music_source)
            self.level_music_player.loop = True
            self.level_music_player.volume = 1.0
            self.level_music_player.play()
        else:
            self.level_music_player = None

        # Иконка ключа
        hud_path = resource_path(os.path.join("assets", "HUD"))
        key_icon_path = os.path.join(hud_path, "key.png")
        if os.path.exists(key_icon_path):
            self.key_icon = arcade.load_texture(key_icon_path)
        else:
            img = Image.new("RGBA", (32, 32), (255, 215, 0, 255))
            self.key_icon = arcade.Texture(name="key_fallback", image=img)

    def restart_level(self):
        self.game_active = True
        self.spinner_player.pause()
        if self.level_music_player:
            self.level_music_player.delete()
        self.setup()

    def on_draw(self):
        self.clear()

        # --- Рисуем мир ---
        self.camera_shake.update_camera()
        self.world_camera.use()
        self.level.draw()
        self.spinner_list.draw()
        self.spinner_half_list.draw()
        self.branacle_list.draw()
        self.slime_green_list.draw()
        self.player_list.draw()
        self.camera_shake.readjust_camera()

        # --- Рисуем GUI ---
        self.gui_camera.use()
        arcade.draw_text(f"Монеты: {self.collected_coins}", 20, self.window.height - 40, arcade.color.YELLOW, 24)
        if self.has_key:
            arcade.draw_texture_rect(
                self.key_icon,
                rect=arcade.LBWH(20, self.window.height - 80, 40, 40)
            )

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
            self.player_sprite.update_animation(delta_time, self.physics_engine, self.is_ducking)

            self.spinner_list.update()
            self.spinner_half_list.update()
            self.branacle_list.update()
            # === Обновление зелёных слаймов ===
            for sl in self.slime_green_list:
                sl.update(delta_time, self.physics_engine)

            # Обновляем камеру
            self.world_camera.position = arcade.math.lerp_2d(
                self.world_camera.position,
                (self.player_sprite.center_x, self.player_sprite.center_y),
                0.1
            )
            self.camera_shake.update(delta_time)

            # === Получаем текущую громкость из БД ===
            from database import get_volume
            current_volume = get_volume()

            # === Применяем к музыке уровня ===
            if self.level_music_player:
                self.level_music_player.volume = current_volume

            all_spinners = list(self.spinner_list) + list(self.spinner_half_list)
            if all_spinners and self.game_active:
                closest_spinner = min(all_spinners, key=lambda s: abs(s.center_x - self.player_sprite.center_x) + abs(
                    s.center_y - self.player_sprite.center_y))
                distance = abs(closest_spinner.center_x - self.player_sprite.center_x) + abs(
                    closest_spinner.center_y - self.player_sprite.center_y)
                max_distance = 3 * 70

                if distance < max_distance:
                    volume = 1.0 - (distance / max_distance)
                    volume = max(0.1, min(1.0, volume))
                    self.spinner_player.volume = volume * current_volume
                    if self.spinner_player.playing is False:
                        self.spinner_player.play()
                    self.last_played_spinner = closest_spinner
                else:
                    self.spinner_player.pause()
                    self.last_played_spinner = None

            # === ПРОВЕРЯЕМ СБОР КЛЮЧА ===
            key_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.level.keys)
            if key_hit_list:
                key = key_hit_list[0]
                key.remove_from_sprite_lists()
                self.has_key = True
                self.key_sound.play(volume=current_volume)

            # === ПРОВЕРЯЕМ ОТКРЫТИЕ БЛОКА (E) ===
            # См. on_key_press

            # Сбор монет
            coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.level.coins)
            for coin in coin_hit_list:
                coin.remove_from_sprite_lists()
                self.collected_coins += 1
                self.coin_sound.play(volume=current_volume)

            # === КОНТАКТ С ЗЕЛЁНЫМИ СЛАЙМАМИ ===
            for sl in self.slime_green_list:
                if arcade.check_for_collision(self.player_sprite, sl):
                    # Проверяем, сверху ли игрок
                    if self.player_sprite.change_y < 0 and self.player_sprite.center_y > sl.center_y:
                        # Прыжок на слайма
                        self.player_sprite.change_y = 8  # отскок
                        sl.squash(self)
                    else:
                        # Боковой контакт — смерть
                        self.trigger_death()
                        self.camera_shake.start()

            # === КОНТАКТ С BRANACLE ===
            branacle_hit = arcade.check_for_collision_with_list(self.player_sprite, self.branacle_list)
            if branacle_hit:
                self.trigger_death()
                self.camera_shake.start()

            # Контакт со шипами → смерть
            spike_hit = arcade.check_for_collision_with_list(self.player_sprite, self.level.spikes)
            if spike_hit:
                self.trigger_death()
                self.camera_shake.start()

            # Контакт с пилами → смерть
            spinner_hit = arcade.check_for_collision_with_list(self.player_sprite, self.spinner_list)
            if spinner_hit:
                self.trigger_death()
                self.camera_shake.start()

            # Контакт с наземными пилами → смерть
            spinner_half_hit = arcade.check_for_collision_with_list(self.player_sprite, self.spinner_half_list)
            if spinner_half_hit:
                self.trigger_death()
                self.camera_shake.start()

            # Конец уровня
            flag_hit = arcade.check_for_collision_with_list(self.player_sprite, self.level.end_flag)
            if flag_hit:
                from database import add_coins
                add_coins(self.collected_coins)
                if self.level_music_player:
                    self.level_music_player.pause()
                elapsed = time.time() - self.start_time
                self.game_active = False
                self.spinner_player.pause()
                self.win_screen = WinScreen(self, elapsed, self.collected_coins)
                return

            # Падение за экран
            if self.player_sprite.center_y < -100:
                self.trigger_death()

    def on_key_press(self, key, modifiers):
        if self.death_screen or self.win_screen:
            return

        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
            return

        if self.paused:
            return

        if key == arcade.key.E:
            if self.has_key:
                # Ищем ближайший KeyBlock в радиусе ~2 тайлов (увеличен до 150)
                closest_block = None
                min_dist = float('inf')
                radius = 150
                for block in self.level.key_blocks:
                    dist = abs(block.center_x - self.player_sprite.center_x) + abs(
                        block.center_y - self.player_sprite.center_y)
                    if dist < min_dist and dist <= radius:
                        min_dist = dist
                        closest_block = block

                if closest_block:
                    closest_block.remove_from_sprite_lists()
                    self.has_key = False  # Ключ потрачен

        if key == arcade.key.LEFT or key == arcade.key.A:
            speed = self.player_sprite.base_speed_x / 2 if self.is_ducking else self.player_sprite.base_speed_x
            self.player_sprite.change_x = -speed
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            speed = self.player_sprite.base_speed_x / 2 if self.is_ducking else self.player_sprite.base_speed_x
            self.player_sprite.change_x = speed
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                jump_power = self.player_sprite.base_jump_y / 2 if self.is_ducking else self.player_sprite.base_jump_y
                self.player_sprite.change_y = jump_power
                # === Прыжок с текущей громкостью ===
                from database import get_volume
                current_volume = get_volume()
                self.jump_sound.play(volume=current_volume)
        elif key == arcade.key.C:
            self.is_ducking = True

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0
        elif key == arcade.key.C:
            self.is_ducking = False

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

    def on_mouse_release(self, x, y, button, modifiers):
        if self.paused:
            self.pause_menu.on_mouse_release(x, y, button, modifiers)

    def trigger_death(self):
        from database import get_player_data
        data = get_player_data()
        self.game_active = False
        self.spinner_player.pause()
        if self.level_music_player:
            self.level_music_player.pause()
        # === Воспроизводим звук смерти с текущей громкостью ===
        from database import get_volume
        current_volume = get_volume()
        self.death_sound.play(volume=current_volume)
        if data["death_screen_enabled"]:
            elapsed = time.time() - self.start_time
            self.death_screen = DeathScreen(self, elapsed, self.collected_coins)
        else:
            self.restart_level()