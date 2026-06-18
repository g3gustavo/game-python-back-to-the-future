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

        # Controle de Estado Estendido
        # Estados possíveis: 'MENU', 'PLAYING', 'GAMEOVER', 'VICTORY'
        self.game_state = "MENU"
        
        # Sistema de Tempo (Fase 1)
        self.level_time = 60 # 60 segundos para passar a Fase 1
        self.time_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self.time_event, 1000) # Evento a cada 1 segundo
        
        # Controle da Fase 2 (Almanaque / Biff)
        self.biff_escaped = False

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

        # Carregamento dos backgrounds de cada fase (800x600)
        self.backgrounds = {}
        try:
            # Mantendo .png já que é o formato original no seu PC!
            self.backgrounds[1] = pygame.image.load("assets/bg_1955.png").convert()
            self.backgrounds[2] = pygame.image.load("assets/bg_2015.png").convert()
            self.backgrounds[3] = pygame.image.load("assets/bg_1885.png").convert()
            print("🖼️ Todos os backgrounds (.png) foram carregados com sucesso!")
        except Exception as e:
            # Se der erro, este print vai te avisar EXATAMENTE qual arquivo falhou
            print(f"⚠️ Erro ao carregar as imagens de fundo: {e}")
            print("Verifique se os nomes na pasta assets/ estão exatamente iguais (ex: bg_1885.png)")

    def reset_game(self, game_over=False):
        """Reseta o estado para uma nova fase ou reinicia tudo em caso de Game Over"""
        if game_over:
            self.current_level = 1
            self.player = Player(100, 400)
            self.level_time = 60 # Reseta o tempo da Fase 1
        else:
            self.player.x = 100
            self.player.y = 400
            self.player.rect.topleft = (100, 400)
            if self.current_level == 2:
                self.level_time = 30 # 🟢 AGORA SÃO 30 SEGUNDOS para pegar o Biff em 2015!
            elif self.current_level == 3:
                self.level_time = 999 # Fase 3 livre para o combate final

        self.enemies = []              
        self.shots = []                
        self.collected_items = 0       
        self.tower_spawned = False
        self.boss_spawned = False
        self.biff_escaped = False
        self.items_on_screen = [Collectible(300, 400), Collectible(500, 300), Collectible(700, 400)]
   
    def check_events(self):
        """Captura os eventos do teclado e do sistema (Método do UML)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            # Eventos nas Telas Finais
            if self.game_state in ["MENU", "GAMEOVER", "VICTORY"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # Enter inicia/reinicia
                        self.reset_game(game_over=True)
                        self.game_state = "PLAYING"
                        
            elif self.game_state == "PLAYING":
                # Reduz o tempo da fase a cada segundo
                if event.type == self.time_event and self.current_level in [1, 2]:
                    self.level_time -= 1
                    if self.level_time <= 0:
                        if self.current_level == 1:
                            print("⏱️ O Tempo acabou! Marty ficou preso in 1955!")
                        else:
                            print("🏃‍♂️ O Tempo acabou! Biff alterou o futuro com o Almanaque!")
                        self.game_state = "GAMEOVER"

                # 💡 CAPTURA DE TECLAS PRESSIONADAS UMA ÚNICA VEZ (PULO E TIRO)
                # Captura de teclas pressionadas uma única vez
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        # Descobre a direção horizontal atual antes de pular
                        keys = pygame.key.get_pressed()
                        direcao = 0
                        if keys[pygame.K_d]: direcao = 1   # Indo para a direita
                        if keys[pygame.K_a]: direcao = -1  # Indo para a esquerda

                        # SE ESTIVER NA FASE 2: Skate voador com impulso horizontal!
                        if self.current_level in [2, 3]:
                            print("🛹 Hoverboard Ativado! Salto Parabólico!")
                            self.player.jump(custom_jump_speed=-21, direction_x=direcao)
                        else:
                            self.player.jump(direction_x=direcao) # Pulo normal
                    
                    # 🟢 ADICIONADO: Lógica para o tiro funcionar novamente!
                    if event.key == pygame.K_SPACE:
                        novo_tiro = self.player.shoot()
                        self.shots.append(novo_tiro)

                # 💡 IDENTAÇÃO CORRIGIDA: O spawn de inimigos deve ficar fora do KEYDOWN
                if event.type == self.SPAWN_ENEMY_EVENT:
                    year_map = {1: 1955, 2: 2015, 3: 1885}
                    fase_ano = year_map.get(self.current_level, 1955)
                    
                    if fase_ano == 1885:
                        if not self.boss_spawned:
                            novo_boss = EnemyFactory.create_boss(750, 370)
                            self.enemies.append(novo_boss)
                            self.boss_spawned = True
                    elif fase_ano == 2015:
                        if not self.boss_spawned:
                            biff_fugitivo = EnemyFactory.create_boss(800, 400)
                            biff_fugitivo.speed = 2
                            self.enemies.append(biff_fugitivo)
                            self.boss_spawned = True
                    else:
                        novo_inimigo = EnemyFactory.create_enemy(fase_ano, 850, 400)
                        self.enemies.append(novo_inimigo)

    def update(self):
        """Atualiza a lógica interna e a física dos personagens"""
        if self.game_state != "PLAYING":
            return # Se não estiver jogando, não atualiza física nem colisões
        
        self.player.update_physics()
        
        # Movimentação de inimigos e verificação de fuga (Fase 2)
        for enemy in self.enemies[:]:
            enemy.update_behavior()
            
            # NOVA REGRA FASE 2: Se o Biff (Boss em 2015) sair da tela pela esquerda, ele escapa!
            if self.current_level == 2 and enemy.x < 0:
                print("🏃‍♂️ Biff escapou com o Almanaque Esportivo!")
                self.game_state = "GAMEOVER"
                return
        
        # Captura as teclas que estão sendo pressionadas continuamente (A e D)
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a]: # Esquerda
            self.player.move(-5, 0)
        if keys[pygame.K_d]: # Direita
            self.player.move(5, 0)
            
        # Remove da lista os inimigos comuns que saíram totalmente da tela pela esquerda
        # Mas atenção: NÃO removemos o Boss se ele sair um pouco, pois ele vai e volta!
        self.enemies = [e for e in self.enemies if e.x > -50 or isinstance(e, Boss)]
        
        # Atualiza a posição de cada tiro
        for shot in self.shots:
            shot.update_behavior()

        # Remove tiros que saíram da tela (X > 800)
        self.shots = [shot for shot in self.shots if shot.x < self.screen_width]

        # ==========================================
        # DETECÇÃO DE COLISÕES
        # ==========================================

        # 1. Tiro atinge Inimigo / Boss
        for shot in self.shots[:]:
            for enemy in self.enemies[:]:
                if shot.rect.colliderect(enemy.rect):
                    # O tiro sempre some ao colidir
                    if shot in self.shots:
                        self.shots.remove(shot)

                    # VERIFICAÇÃO POLIMÓRFICA: Se for um Boss (Biff ou Buford Tannen)
                    if isinstance(enemy, Boss):
                        # 🛹 Fase 2: Biff sempre imune a tiros (é derrotado no corpo a corpo)
                        if self.current_level == 2:
                            print("🛡️ O Biff está protegido! Você precisa pegar os 3 capacitores e alcançá-lo!")
                        
                        # 🤠 Fase 3: Buford Tannen só toma dano se tiver os 3 capacitores!
                        elif self.current_level == 3:
                            if self.collected_items < 3:
                                print("🛡️ Buford Tannen ri do seu tiro! Pegue os 3 capacitores para fazer efeito!")
                            else:
                                morreu = enemy.take_damage()
                                print(f"🤠 Chefe atingido! HP restante: {enemy.hp}")
                                
                                if morreu:
                                    if enemy in self.enemies:
                                        self.enemies.remove(enemy)
                                    self.player.score += 1000 # Super bônus!
                                    print("🏆 VITÓRIA TEMPORAL TOTAL!")
                                    self.game_state = "VICTORY"
                    else:
                        # Inimigo comum (capangas) morre com 1 tiro só
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                        self.player.score += 100
                        print(f"Inimigo derrotado! Pontuação: {self.player.score}")

                    break # Sai do loop interno de inimigos já que o tiro sumiu

        # 2. Inimigo atinge o Player
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                
                # LÓGICA DA FASE 2 (BIFF)
                if self.current_level == 2 and isinstance(enemy, Boss):
                    if self.collected_items < 3:
                        self.player.take_damage()
                        print(f"Marty trombou no Biff sem os capacitores! Vidas: {self.player.lives}")
                        self.player.move(-40, 0) # Empurra para trás
                    else:
                        print("💥 Marty recuperou o Almanaque das mãos do Biff!")
                        print("Avançando para a Fase 3 (1885)!")
                        self.current_level = 3
                        self.reset_game(game_over=False)
                        return # Interrompe para carregar a nova fase com segurança

                # 🤠 NOVA LÓGICA DA FASE 3 (BUFORD TANNEN)
                elif self.current_level == 3 and isinstance(enemy, Boss):
                    if self.collected_items < 3:
                        # Se bater nele antes de pegar os capacitores: GAME OVER DIRETO!
                        print("💥 Buford pegou Marty desprevenido sem os capacitores! Fim da linha!")
                        self.player.lives = 0 
                    else:
                        # Se já pegou os itens, ele age como obstáculo perigoso tirando dano normal
                        self.player.take_damage()
                        self.player.move(-50, 0) # Empurra para trás para dar espaço
                        print(f"Marty trombou no Buford! Vidas restantes: {self.player.lives}")
                
                # Capangas comuns de qualquer fase
                else:
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.player.take_damage()
                    print(f"Marty foi atingido por um capanga! Vidas restantes: {self.player.lives}")
                
                # Verifica se o jogador morreu (seja por zerar vidas ou pelo hit kill do Buford)
                if self.player.lives <= 0:
                    print("GAME OVER!")
                    self.db.save_score("Marty McFly", self.player.score) 
                    self.reset_game(game_over=True)
                    self.game_state = "GAMEOVER"
                    return

        # 3. Coleta de Itens (Capacitor de Fluxo)
        for item in self.items_on_screen[:]:
            if item.rect.colliderect(self.player.rect):
                self.items_on_screen.remove(item)
                self.collected_items += 1
                self.player.score += 200 
                print(f"Item coletado! {self.collected_items}/3 Capacitores de Fluxo.")

        # Se coletou os 3, ativa a torre (Apenas útil na Fase 1)
        if self.collected_items == 3:
            self.tower_spawned = True

        # 4. Condição de Vitória e Transição de Fases (Apenas Fase 1)
        if self.tower_spawned and self.current_level == 1: 
            if self.player.rect.colliderect(self.clock_tower.rect):
                print("Avançando para a Fase 2 (2015)!")
                self.current_level = 2
                self.reset_game(game_over=False)

        # 2. Inimigo atinge o Player
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                # 🟢 NOVA LÓGICA COERENTE DA FASE 2 (BIFF)
                if self.current_level == 2 and isinstance(enemy, Boss):
                    if self.collected_items < 3:
                        self.player.take_damage()
                        print(f"Marty trombou no Biff sem os capacitores! Vidas: {self.player.lives}")
                        self.player.move(-40, 0) # Empurra para trás
                    else:
                        # 🛹 VITÓRIA DA FASE: Pegou os 3 itens e alcançou o Biff!
                        print("💥 Marty recuperou o Almanaque das mãos do Biff!")
                        print("Avançando para a Fase 3 (1885)!")
                        self.current_level = 3
                        self.reset_game(game_over=False)
                        break # Sai do loop para evitar erros de colisão no mesmo frame
                else:
                    # Comportamento normal para capangas comuns: somem ao dar dano
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.player.take_damage()
                    print(f"Marty foi atingido! Vidas restantes: {self.player.lives}")
                
                if self.player.lives <= 0:
                    print("GAME OVER!")
                    self.db.save_score("Marty McFly", self.player.score) 
                    self.reset_game(game_over=True)
                    self.game_state = "GAMEOVER"

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

        # 4. Condição de Vitória e Transição de Fases
        if self.tower_spawned and self.current_level == 1: 
            if self.player.rect.colliderect(self.clock_tower.rect):
                print("Avançando para a Fase 2 (2015)!")
                self.current_level = 2
                self.reset_game(game_over=False)

    def draw(self):
        """Renderiza os elementos gráficos na tela (Método do UML)"""
        self.screen.fill((0, 0, 0))
        
        if self.game_state == "MENU":
            title_text = self.title_font.render("BACK TO THE FUTURE: TIME CRISIS", True, (255, 128, 0))
            instruct_text = self.font.render("Pressione [ENTER] para Iniciar o Jogo", True, (255, 255, 255))
            
            cmd_w = self.font.render("[W] - Pular", True, (200, 200, 200))
            cmd_ad = self.font.render("[A / D] - Mover para os Lados", True, (200, 200, 200))
            cmd_space = self.font.render("[ESPAÇO] - Atirar", True, (200, 200, 200))
            
            score_title = self.font.render("--- TOP RECORDES ---", True, (255, 255, 0))
            self.screen.blit(title_text, (50, 80))
            self.screen.blit(instruct_text, (180, 180))
            self.screen.blit(cmd_w, (280, 260))
            self.screen.blit(cmd_ad, (280, 300))
            self.screen.blit(cmd_space, (280, 340))
            self.screen.blit(score_title, (270, 410))
            
            # Tenta buscar os recordes do banco
            try:
                top_scores = self.db.get_top_scores(3)
                y_offset = 450
                for idx, row in enumerate(top_scores):
                    row_text = self.font.render(f"{idx+1}. {row[0]} - {row[1]} pts", True, (0, 255, 255))
                    self.screen.blit(row_text, (300, y_offset))
                    y_offset += 35
            except:
                pass
            
        elif self.game_state == "GAMEOVER":
            title_text = self.title_font.render("GAME OVER", True, (255, 0, 0))
            sub_text = self.font.render("A linha do tempo foi destruida!", True, (200, 200, 200))
            restart_text = self.font.render("Pressione [ENTER] para tentar novamente", True, (255, 255, 255))
            self.screen.blit(title_text, (280, 180))
            self.screen.blit(sub_text, (230, 260))
            self.screen.blit(restart_text, (160, 340))

        elif self.game_state == "VICTORY":
            title_text = self.title_font.render("VITÓRIA TEMPORAL!", True, (0, 255, 0))
            sub_text = self.font.render("Doc e Marty voltaram para 1985 em seguranca!", True, (200, 200, 200))
            restart_text = self.font.render("Pressione [ENTER] para jogar novamente", True, (255, 255, 255))
            self.screen.blit(title_text, (200, 180))
            self.screen.blit(sub_text, (130, 260))
            self.screen.blit(restart_text, (160, 340))

        elif self.game_state == "PLAYING":
            # 🖼️ NOVIDADE: Desenha o fundo da fase atual se ele existir, senão usa preto
            if self.current_level in self.backgrounds:
                self.screen.blit(self.backgrounds[self.current_level], (0, 0))
            else:
                self.screen.fill((0, 0, 0)) # Fundo reserva caso falte a imagem
            
            # Desenha elementos do jogo por cima do fundo...
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for shot in self.shots:
                shot.draw(self.screen)
            for item in self.items_on_screen:
                item.draw(self.screen)
            if self.tower_spawned and self.current_level == 1:
                self.clock_tower.draw(self.screen)
                
            # Renderiza HUD de Vidas, Pontos e o Novo Contador de Tempo
            score_display = self.font.render(f"Pontos: {self.player.score}", True, (255, 255, 255))
            lives_display = self.font.render(f"Vidas: {self.player.lives}", True, (255, 0, 0))
            self.screen.blit(score_display, (20, 20))
            self.screen.blit(lives_display, (650, 20))
            
            # MOSTRAR O TEMPO NA FASE 1 E NA FASE 2
            if self.current_level in [1, 2]:
                time_display = self.font.render(f"Tempo: {self.level_time}s", True, (255, 255, 0))
                self.screen.blit(time_display, (350, 20))
                
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