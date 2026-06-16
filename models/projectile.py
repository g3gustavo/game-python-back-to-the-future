import pygame
from models.entity import Entity

class Shot(Entity):
    def __init__(self, x: int, y: int, speed: int = 10):
        # Inicializa a entidade base (x, y) sem imagem por enquanto (bloco amarelo)
        super().__init__(x, y)
        
        # Define o tamanho do tiro (um retângulo menor amarelo)
        self.image = pygame.Surface((15, 5))
        self.image.fill((255, 255, 0)) # Amarelo
        
        # Atualiza o rect com o novo tamanho
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Velocidade do tiro (vai para a direita, então é positiva)
        self.speed = speed

    def update_behavior(self):
        """Move o tiro continuamente para a direita"""
        self.move(self.speed, 0)