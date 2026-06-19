import pygame
from models.entity import Entity

class Collectible(pygame.sprite.Sprite): # Ou a classe mãe que ela herdar
    def __init__(self, x: int, y: int, image_surface=None):
        super().__init__()
        self.image = image_surface
        
        # Se nenhuma imagem for passada agora, criamos um rect temporário.
        # O Game.py vai substituir essa imagem e o rect logo em seguida!
        if self.image:
            self.rect = self.image.get_rect()
        else:
            self.rect = pygame.Rect(x, y, 40, 40) # Tamanho padrão de segurança
            
        self.rect.topleft = (x, y)
        
    def draw(self, screen):
        # Só desenha se a imagem já tiver sido carregada pelo Game
        if self.image:
            screen.blit(self.image, self.rect)

class Tower(Entity):
    def __init__(self, x: int, y: int):
        # Carrega a imagem da Torre do Relógio (ex: tower.png)
        super().__init__(x, y, image_path="assets/tower.png")