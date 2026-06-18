import pygame
from models.entity import Entity

class Collectible(Entity):
    def __init__(self, x: int, y: int):
        # Carrega a imagem do item (ex: capacitor.png) via caminho relativo
        super().__init__(x, y, image_path="assets/capacitor.png")

class Tower(Entity):
    def __init__(self, x: int, y: int):
        # Carrega a imagem da Torre do Relógio (ex: tower.png)
        super().__init__(x, y, image_path="assets/tower.png")