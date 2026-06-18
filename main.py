import pygame
import sys
from models.characters import Player, Enemy, Boss
from models.projectile import Shot
from models.factory import EnemyFactory
from models.database import DatabaseProxy
from models.scenery import Collectible, Tower

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

        # Controle de Itens do Capacitor de Fluxo
        self.collected_items = 0
        self.items_on_screen = [
            Collectible(300, 400), # Item 1
            Collectible(500, 300), # Item 2 (mais alto para pular)
            Collectible(700, 400)  # Item 3
        ]

        # Instancia a Torre do Relógio no final do cenário (fora da tela inicialmente)
        self.clock_tower = Tower(750, 350) 
        self.tower_spawned = False

        # Controle para garantir que o Boss só apareça uma vez por fase (pode ser usado futuramente para a Fase 3)
        self.boss_spawned = False

    def reset_game(self, game_over=False):
        """Reseta o estado para uma nova fase ou reinicia tudo em caso de Game Over"""
        if game_over:
            self.current_level = 1
            self.player = Player(100, 400)
        else:
            # Mantém os pontos e vidas do Marty, mas reseta a posição dele no começo da tela
            self.player.x = 100
            self.player.y = 400
            self.player.rect.topleft = (100, 400)

        self.enemies = []              # Limpa os inimigos da fase anterior
        self.shots = []                # Limpa os tiros da fase anterior
        self.collected_items = 0       # Zera os itens para a nova fase
        self.tower_spawned = False
        self.boss_spawned = False
        
        # Recria os itens para a nova fase (podem ser em posições diferentes no futuro!)
        self.items_on_screen = [Collectible(300, 400), Collectible(500, 300), Collectible(700, 400)]
    
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
                    year_map = {1: 1955, 2: 2015, 3: 1885}
                    fase_ano = year_map.get(self.current_level, 1955)

                    if fase_ano == 1885:
                        # Se for o Velho Oeste e o Boss ainda não nasceu, invoca ele!
                        if not self.boss_spawned:
                            novo_boss = EnemyFactory.create_boss(750, 370) # Y um pouco mais alto porque ele é maior
                            self.enemies.append(novo_boss)
                            self.boss_spawned = True
                    else:
                        # Nas fases 1 e 2, nascem os capangas/drones normais a cada 2s
                        novo_inimigo = EnemyFactory.create_enemy(fase_ano, 850, 400)
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

        # 1. Tiro atinge Inimigo / Boss
        for shot in self.shots[:]:
            for enemy in self.enemies[:]:
                if shot.rect.colliderect(enemy.rect):
                    self.shots.remove(shot)

                    # 🟢 VERIFICAÇÃO POLIMÓRFICA: Se for o Boss, rodamos o take_damage dele
                    if isinstance(enemy, Boss):
                        morreu = enemy.take_damage()
                        print(f"🤠 Buford Tannen foi atingido! HP restante: {enemy.hp}")
                        if morreu:
                            self.enemies.remove(enemy)
                            self.player.score += 1000 # Super bônus!
                            print("🏆 VITÓRIA TEMPORAL! Você derrotou o Cachorro Louco!")
                            self.game_state = "MENU" # Volta pro menu vitorioso
                            self.reset_game(game_over=True) 
                    else:
                        # Inimigo comum morre com 1 tiro só
                        self.enemies.remove(enemy)
                        self.player.score += 100
                        print(f"Inimigo derrotado! Pontuação: {self.player.score}")

                    break

        # 2. Inimigo atinge o Player
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                self.enemies.remove(enemy)
                self.player.take_damage()
                print(f"Marty foi atingido! Vidas restantes: {self.player.lives}")
                
                if self.player.lives <= 0:
                    print("GAME OVER!")
                    self.db.save_score("Marty McFly", self.player.score) 
                    self.reset_game(game_over=True) # 🟢 Reseta tudo para o nível 1
                    self.game_state = "MENU"

        # 3. Coleta de Itens (Capacitor de Fluxo)
        for item in self.items_on_screen[:]:
            if item.rect.colliderect(self.player.rect):
                self.items_on_screen.remove(item)
                self.collected_items += 1
                self.player.score += 200 # Bônus por coletar
                print(f"Item coletado! {self.collected_items}/3 Capacitores de Fluxo.")

        # Se coletou os 3, a Torre do Relógio se torna "ativa/visível"
        if self.collected_items == 3:
            self.tower_spawned = True

        # 4. Condição de Vitória da Fase 1 e Transição
        if self.tower_spawned:
            if self.player.rect.colliderect(self.clock_tower.rect):
                if self.current_level == 1:
                    print("⚡ Avançando para a Fase 2 (2015)!")
                    self.current_level = 2
                    self.reset_game(game_over=False) # Limpa a tela mantendo os dados do player
                    # Continuamos no estado 'PLAYING', o jogo não para!
                
                elif self.current_level == 2:
                    print("⚡ Avançando para a Fase 3 (1885)!")
                    self.current_level = 3
                    self.reset_game(game_over=False)

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
            # Desenha o Player, os inimigos, os tiros e os itens na tela durante a gameplay
            self.player.draw(self.screen) # Desenha o Player na tela
            for enemy in self.enemies:
                enemy.draw(self.screen) # Desenha cada inimigo na tela
            for shot in self.shots:
                shot.draw(self.screen) # Desenha cada tiro na tela
            for item in self.items_on_screen:
                item.draw(self.screen) # Desenha os itens do Capacitor de Fluxo na tela
            if self.tower_spawned:
                self.clock_tower.draw(self.screen) # Desenha a Torre do Relógio se ela tiver sido "ativada" (coletou os 3 itens)

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