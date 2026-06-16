import pygame
from models.entity import Entity
from models.projectile import Shot

class Player(Entity):
    def __init__(self, x: int, y: int):
        # Chamamos o construtor da classe mãe (Entity)
        super().__init__(x, y)
        
        # Mudamos a cor do bloco do Player para Verde para sabermos quem é quem no teste
        self.image.fill((0, 255, 0))
        
        # Atributos específicos do Player definidos no seu UML
        self.lives = 3
        self.score = 0
        self.is_jumping = False
        self.jump_speed = -15
        self.gravity = 1
        self.velocity_y = 0

    def jump(self):
        """Lógica do pulo (W)"""
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_speed

    def update_physics(self):
        """Aplica gravidade ao pulo do jogador"""
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            
            # Chão temporário para o bloco não cair no infinito
            if self.y >= 400: 
                self.y = 400
                self.is_jumping = False
                self.velocity_y = 0
                
            self.rect.topleft = (self.x, self.y)

    def shoot(self):
        """Instancia um novo tiro saindo da frente do jogador"""
        # Cria o tiro na ponta direita do rect do player e centralizado na altura
        tiro = Shot(self.rect.right, self.rect.centery - 2)
        return tiro

    def take_damage(self):
        """Reduz a vida do jogador"""
        self.lives -= 1


class Enemy(Entity):
    def __init__(self, x: int, y: int, speed: int = 5):
        super().__init__(x, y)
        
        # Mudamos a cor do bloco do Inimigo para Vermelho (Capangas do Biff)
        self.image.fill((255, 0, 0))
        
        # Atributo específico do Inimigo definido no seu UML
        self.speed = speed

    def update_behavior(self):
        """Faz o inimigo andar automaticamente para a esquerda"""
        self.move(-self.speed, 0)