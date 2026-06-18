import pygame
from models.entity import Entity
from models.projectile import Shot

class Player(Entity):
    def __init__(self, x: int, y: int):
        # Chamamos o construtor da classe mãe (Entity)
        super().__init__(x, y, image_path="assets/player.png")
              
        # Atributos específicos do Player definidos no seu UML
        self.lives = 3
        self.score = 0
        self.is_jumping = False
        self.jump_speed = -15
        self.gravity = 1
        self.velocity_y = 0

    def jump(self, custom_jump_speed: int = None, direction_x: int = 0):
        """Lógica do pulo (W) - Aceita velocidade customizada e impulso horizontal"""
        if not self.is_jumping:
            self.is_jumping = True
            
            # 1. Ajusta a altura do pulo (Eixo Y)
            if custom_jump_speed is not None:
                self.velocity_y = custom_jump_speed
            else:
                self.velocity_y = self.jump_speed

            # 2. 🛹 NOVIDADE: Dá impulso para frente (Eixo X) baseado na direção atual
            # Se for na Fase 2 (impulso customizado), o empurrão para a frente é ainda maior!
            if custom_jump_speed is not None: 
                self.velocity_x = direction_x * 8  # Impulso forte do Hoverboard
            else:
                self.velocity_x = direction_x * 4  # Impulso normal na Fase 1

    def update_physics(self):
        """Aplica gravidade e inércia horizontal ao pulo do jogador"""
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            self.x += self.velocity_x # 🛹 Aplica o impulso horizontal no ar!
            
            # Chão temporário
            if self.y >= 400: 
                self.y = 400
                self.is_jumping = False
                self.velocity_y = 0
                self.velocity_x = 0 # Para de se mover ao tocar o chão
                
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
        super().__init__(x, y, image_path="assets/enemy.png")
        
        # Atributo específico do Inimigo definido no seu UML
        self.speed = speed

    def update_behavior(self):
        """Faz o inimigo andar automaticamente para a esquerda"""
        self.move(-self.speed, 0)

class Boss(Enemy):
    def __init__(self, x: int, y: int):
        # O Boss começa com velocidade 3, mas vamos carregar o sprite dele do Velho Oeste
        super().__init__(x, y, speed=3)
        
        # 🟢 ESPECIALIZAÇÃO: O Boss usa uma imagem própria
        # (Se não tiver a imagem ainda, a classe mãe Entity cria o bloco padrão)
        try:
            self.image = pygame.image.load("assets/boss.png").convert_alpha()
        except:
            self.image = pygame.Surface((80, 80)) # O Boss é maior que os capangas!
            self.image.fill((139, 0, 0)) # Vermelho Escuro / Marrom
            
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Atributos exclusivos do Chefe do seu UML
        self.hp = 5 # O Boss precisa levar 5 tiros para morrer!
        self.special_timer = 0

    def update_behavior(self):
        """Faz o Boss se movimentar de um jeito diferente (vai e volta na tela)"""
        self.move(-self.speed, 0)
        
        # Se ele chegar muito perto do Marty, ele recua um pouco para continuar atirando/atacando
        if self.x < 400:
            self.speed = -2 # Muda a direção para a direita
        if self.x > 750:
            self.speed = 2  # Muda a direção de volta para a esquerda

    def special_attack(self):
        """Lógica para o ataque especial (será mapeado na IA/Sprint Final se necessário)"""
        pass

    def take_damage(self):
        """O Boss perde 1 ponto de vida por tiro"""
        self.hp -= 1
        return self.hp <= 0 # Retorna True se o Boss morreu
    
