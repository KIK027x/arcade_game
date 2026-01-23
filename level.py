import arcade
from arcade import load_tilemap

class Level:
    def __init__(self, map_path):
        self.tile_map = load_tilemap(map_path)
        self.scene = self.tile_map.sprite_lists

        self.platforms = self.scene.get("Platforms", arcade.SpriteList())
        self.coins = self.scene.get("coins", arcade.SpriteList())
        self.end_flag = self.scene.get("EndFlag", arcade.SpriteList())

    def draw(self):
        for sprite_list in self.scene.values():
            sprite_list.draw()
