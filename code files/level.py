import arcade
from arcade import load_tilemap

class Level:
    def __init__(self, map_path):
        self.tile_map = load_tilemap(map_path)
        self.scene = self.tile_map.sprite_lists

        # Слои спрайтов
        self.platforms = self.scene.get("Platforms", arcade.SpriteList())
        self.coins = self.scene.get("Coins", arcade.SpriteList())
        self.spikes = self.scene.get("Spikes", arcade.SpriteList())
        self.end_flag = self.scene.get("EndFlag", arcade.SpriteList())
        self.spinners = self.scene.get("Spinner", arcade.SpriteList())
        self.spinner_half = self.scene.get("SpinnerHalf", arcade.SpriteList())
        self.keys = self.scene.get("Key", arcade.SpriteList())
        self.key_blocks = self.scene.get("KeyBlock", arcade.SpriteList())
        self.branacles = self.scene.get("Branacle", arcade.SpriteList())
        self.slimes_green = self.scene.get("SlimeGreen", arcade.SpriteList())

    def draw(self):
        for sprite_list in self.scene.values():
            sprite_list.draw()