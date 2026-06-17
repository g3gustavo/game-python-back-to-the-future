import pygame
import sys
from models.characters import Player, Enemy
from models.projectile import Shot
from models.factory import EnemyFactory
from models.database import DatabaseProxy

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

        # Inicializa o Proxy do Banco de Dados
        self.db = DatabaseProxy()

        # Controle de Estado do Jogo: 'MENU' ou 'PLAYING'
        self.game_state = "MENU"

        # Inicialização de Fontes para escrever textos na tela
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 50, bold=True)

    def reset_game(self):
        """Reseta o estado do jogo para uma nova partida"""
        self.player = Player(100, 400) # Cria um novo Player com 3 vidas e score 0
        self.enemies = []              # Limpa os inimigos antigos da tela
        self.shots = []                # Limpa os tiros antigos
    
    def check_events(self):
        """Captura os eventos do teclado e do sistema (Método do UML)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            # Eventos se estiver no MENU
            if self.game_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # Apertou Enter, começa o jogo
                        self.game_state = "PLAYING"

            # Eventos se estiver JOGANDO )
            elif self.game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.player.jump()
                    if event.key == pygame.K_SPACE:
                        novo_tiro = self.player.shoot()
                        self.shots.append(novo_tiro)

                if event.type == self.SPAWN_ENEMY_EVENT:
                    novo_inimigo = EnemyFactory.create_enemy(self.current_level * 1955, 850, 400)
                    self.enemies.append(novo_inimigo)

    def update(self):
        """Atualiza a lógica interna e a física dos personagens"""
        if self.game_state != "PLAYING":
            return # Se não estiver jogando, não atualiza física nem colisões
        
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
                self.player.take_damage()
                print(f"Marty foi atingido! Vidas restantes: {self.player.lives}")
                
                if self.player.lives <= 0:
                    print("GAME OVER! Voltando para o Menu Principal...")
                    # Salva o recorde no banco SQLite via Proxy
                    self.db.save_score("Marty McFly", self.player.score) 
                    
                    # Em vez de fechar o jogo, reseta e volta pro Menu!
                    self.reset_game()
                    self.game_state = "MENU"


    def draw(self):
        """Renderiza os elementos gráficos na tela (Método do UML)"""
        self.screen.fill((0, 0, 0)) # Fundo preto

        if self.game_state == "MENU":
            # Desenha a tela de Menu Inicial e Instruções Obrigatórias do trabalho
            title_text = self.title_font.render("BACK TO THE FUTURE: TIME CRISIS", True, (255, 128, 0))
            instruct_text = self.font.render("Pressione [ENTER] para Iniciar o Jogo", True, (255, 255, 255))

            # Comandos Obrigatórios escritos textualmente na tela
            cmd_w = self.font.render("[W] - Pular", True, (200, 200, 200))
            cmd_ad = self.font.render("[A / D] - Mover para os Lados", True, (200, 200, 200))
            cmd_space = self.font.render("[ESPAÇO] - Atirar", True, (200, 200, 200))

            # Renderiza os recordes do Banco de Dados no Menu!
            score_title = self.font.render("--- TOP RECORDES ---", True, (255, 255, 0))
            self.screen.blit(title_text, (50, 80))
            self.screen.blit(instruct_text, (180, 180))
            self.screen.blit(cmd_w, (280, 260))
            self.screen.blit(cmd_ad, (280, 300))
            self.screen.blit(cmd_space, (280, 340))
            self.screen.blit(score_title, (270, 410))

            # Loop para listar os recordes vindos do SQLite
            top_scores = self.db.get_top_scores(3)
            y_offset = 450
            for idx, row in enumerate(top_scores):
                row_text = self.font.render(f"{idx+1}. {row[0]} - {row[1]} pts", True, (0, 255, 255))
                self.screen.blit(row_text, (300, y_offset))
                y_offset += 35

        elif self.game_state == "PLAYING":
            # Desenha os elementos do jogo que você já fez
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for shot in self.shots:
                shot.draw(self.screen)

        # Desenha o Placar e as Vidas na tela durante a gameplay
        score_display = self.font.render(f"Pontos: {self.player.score}", True, (255, 255, 255))
        lives_display = self.font.render(f"Vidas: {self.player.lives}", True, (255, 0, 0))
        self.screen.blit(score_display, (20, 20))
        self.screen.blit(lives_display, (650, 20))

        pygame.display.flip()

    def run_game(self):
        """Inicia o loop principal do jogo (Método do UML)"""
        while self.is_running:
            self.check_events()
            self.update()
            self.draw()
            self.clock.tick(60) # Limita o jogo a 60 FPS
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Instancia o objeto do jogo e inicia o loop
    game = Game()
    game.run_game()