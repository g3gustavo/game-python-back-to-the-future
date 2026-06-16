import pygame

class Entity:
    def __init__(self, x: int, y: int, image_path: str = None):
        # Atributos base que você definiu no UML
        self.x = x
        self.y = y
        
        # Se passarmos um caminho de imagem relativo, carregamos ela. 
        # Se não, criamos um bloco temporário para podermos testar sem gráficos.
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            # Bloco temporário caso não tenha imagem ainda
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 255, 255)) # Branco padrão
            
        # O 'rect' que você corrigiu no UML! Essencial para posições e colisões no PyGame
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def move(self, dx: int, dy: int):
        """Método base para movimentação na tela"""
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen: pygame.Surface):
        """Desenha a entidade na janela do jogo"""
        screen.blit(self.image, self.rect)