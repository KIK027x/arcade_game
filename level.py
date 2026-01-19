import arcade
from arcade import load_tilemap

class Level:
    def __init__(self, map_path):
        # Загружаем карту
        self.tile_map = load_tilemap(map_path)
        self.scene = self.tile_map.sprite_lists

        # Получаем тайловый слой Platforms как список спрайтов
        self.platforms = self.scene.get("Platforms", arcade.SpriteList())

        # Отладка
        print("Платформы:", len(self.platforms))

    def draw(self):
        # Рисуем всё
        for sprite_list in self.scene.values():
            sprite_list.draw()