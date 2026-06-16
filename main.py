import pygame
import sys
from models.characters import Player, Enemy
from models.projectile import Shot
from models.factory import EnemyFactory

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
        self.enemies = []

        # Lista para armazenar os tiros ativos na tela
        self.shots = []

        # Criando um evento personalizado para spawnar inimigos a cada 2 segundos
        self.SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_ENEMY_EVENT, 2000) # Dispara a cada 2000ms

    def check_events(self):
        """Captura os eventos do teclado e do sistema (Método do UML)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.player.jump()
                if event.key == pygame.K_SPACE:
                    novo_tiro = self.player.shoot()
                    self.shots.append(novo_tiro)

            # Captura o sinal do relógio para criar inimigos
            if event.type == self.SPAWN_ENEMY_EVENT:
                # Usamos a fábrica para gerar na borda direita (X=850) no chão (Y=400)
                # Teste mudar o ano para 2015 ou 1885 para ver o comportamento mudar!
                novo_inimigo = EnemyFactory.create_enemy(self.current_level * 2015, 850, 400)
                self.enemies.append(novo_inimigo)

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
        
        # Atualiza cada inimigo gerado pela fábrica individualmente
        for enemy in self.enemies:
            enemy.update_behavior()
            
        # Remove da lista os inimigos que saíram totalmente da tela pela esquerda
        self.enemies = [enemy for enemy in self.enemies if enemy.x > -50]
        
        # Atualiza a posição de cada tiro
        for shot in self.shots:
            shot.update_behavior()

        # List Comprehension para remover tiros que saíram da tela (X > 800)
        self.shots = [shot for shot in self.shots if shot.x < self.screen_width]

        #DETECÇÃO DE COLISÕES

        # 1. Tiro atinge Inimigo
        for shot in self.shots[:]: # Usamos [:] para fazer uma cópia da lista e evitar bugs ao remover itens
            for enemy in self.enemies[:]:
                if shot.rect.colliderect(enemy.rect):
                    self.shots.remove(shot)
                    self.enemies.remove(enemy)
                    self.player.score += 100 # Ganha pontos!
                    print(f"Inimigo derrotado! Pontuação: {self.player.score}")
                    break # Sai do loop interno do inimigo já que o tiro sumiu

        # 2. Inimigo atinge o Player
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                self.enemies.remove(enemy)
                self.player.take_damage() # Perde vida!
                print(f"Marty foi atingido! Vidas restantes: {self.player.lives}")
                
                if self.player.lives <= 0:
                    print("GAME OVER! A linha do tempo foi destruída!")
                    self.is_running = False # Fecha o jogo se perder todas as vidas


    def draw(self):
        """Renderiza os elementos gráficos na tela (Método do UML)"""
        self.screen.fill((0, 0, 0)) # Fundo preto clássico de espaço/fase inicial
        
        # Desenha o Player (Bloco Verde) e o Inimigo (Bloco Vermelho)
        self.player.draw(self.screen)
        # Desenha todos os inimigos ativos
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Desenha todos os tiros ativos
        for shot in self.shots:
            shot.draw(self.screen)
        
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