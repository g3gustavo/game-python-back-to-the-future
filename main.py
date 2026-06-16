import pygame
import sys
from models.characters import Player, Enemy

class Game:
    def __init__(self):
        pygame.init()
        
        # Configuração da janela do jogo (Atributo do seu UML)
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Back to the Future: Time Crisis")
        
        # Controladores do Loop (Atributos do seu UML)
        self.current_level = 1
        self.is_running = True
        self.clock = pygame.time.Clock()
        
        # Instanciando o Player na posição X=100, Y=400 (Chão temporário)
        self.player = Player(100, 400)
        
        # Criando um inimigo de teste para ver se ele aparece na tela
        self.test_enemy = Enemy(600, 400, speed=2)

    def check_events(self):
        """Captura os eventos do teclado e do sistema (Método do UML)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                
            # Evento de clique único para o Pulo (W)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.player.jump()

    def update(self):
        """Atualiza a lógica interna e a física dos personagens"""
        # Captura as teclas que estão sendo pressionadas continuamente (A e D)
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a]: # Esquerda
            self.player.move(-5, 0)
        if keys[pygame.K_d]: # Direita
            self.player.move(5, 0)
            
        # Atualiza a gravidade do pulo do jogador
        self.player.update_physics()
        
        # Faz o inimigo de teste andar sozinho para a esquerda
        self.test_enemy.update_behavior()
        
        # Se o inimigo sair da tela, reseta ele na direita para podermos continuar testando
        if self.test_enemy.x < -50:
            self.test_enemy.x = 800
            self.test_enemy.y = 400

    def draw(self):
        """Renderiza os elementos gráficos na tela (Método do UML)"""
        self.screen.fill((0, 0, 0)) # Fundo preto clássico de espaço/fase inicial
        
        # Desenha o Player (Bloco Verde) e o Inimigo (Bloco Vermelho)
        self.player.draw(self.screen)
        self.test_enemy.draw(self.screen)
        
        pygame.display.flip()

    def run_game(self):
        """Inicia o loop principal do jogo (Método do UML)"""
        while self.is_running:
            self.check_events()
            self.update()
            self.draw()
            
            self.clock.tick(60) # Limita o jogo a 60 Frames Por Segundo (FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Instancia o objeto do jogo e inicia o loop
    game = Game()
    game.run_game()