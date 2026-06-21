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

        # Inicializa o sistema de áudio (geralmente já vem junto com o pygame.init())
        pygame.mixer.init()

        # 1. CARREGAR EFEITOS SONOROS (Objetos Sound)
        self.som_pulo = pygame.mixer.Sound("sons/pulo.wav")
        self.som_tiro = pygame.mixer.Sound("sons/tiro.wav")
        
        # Ajuste de volume individual se precisar (0.0 até 1.0)
        self.som_pulo.set_volume(0.5)
        self.som_tiro.set_volume(0.4)

        # 2. SELEÇÃO DE MÚSICAS DE FUNDO (Dicionário para facilitar as fases)
        self.musica_jogo = "sons/musica_geral.mp3"
        self.musica_gameover = "sons/musica_gameover.mp3"
        self.musica_vitoria = "sons/musica_vitoria.mp3"
        
        # Configuração da janela do jogo
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Back to the Future: Time Crisis")
                
        # Controladores do Loop
        self.current_level = 1
        self.is_running = True
        self.clock = pygame.time.Clock()
        
        # Instanciando o Player
        self.player = Player(20, 430)
        self.enemies = []
        self.shots = []

        # Evento para spawnar inimigos
        self.SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_ENEMY_EVENT, 2000)

        # Banco de Dados e Estados
        self.db = DatabaseProxy()
        self.game_state = "MENU"
        
        # Sistema de Tempo
        self.level_time = 60 
        self.time_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self.time_event, 1000)
        
        self.biff_escaped = False

        # Fontes
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 50, bold=True)

        self.clock_tower = Tower(650, 430) 
        self.tower_spawned = False
        self.boss_spawned = False

        # Carregamento dos backgrounds
        self.backgrounds = {}
        try:
            self.backgrounds[1] = pygame.image.load("assets/bg_1955.png").convert()
            self.backgrounds[2] = pygame.image.load("assets/bg_2015.png").convert()
            self.backgrounds[3] = pygame.image.load("assets/bg_1885.png").convert()
            print("🖼️ Todos os backgrounds (.png) foram carregados com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao carregar as imagens de fundo: {e}")

        # Carregamento e Redimensionamento das imagens dos itens
        self.item_images = {}
        try:
            self.item_images[1] = pygame.transform.scale(pygame.image.load("assets/capacitor.png").convert_alpha(), (40, 40))
            self.item_images[2] = pygame.transform.scale(pygame.image.load("assets/almanaque.png").convert_alpha(), (40, 40))
            self.item_images[3] = pygame.transform.scale(pygame.image.load("assets/foto.png").convert_alpha(), (40, 40))
            print("🔋 Itens das fases carregados com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao carregar imagens dos itens: {e}")

        # Controle de Itens e Spawn Inicial
        self.collected_items = 0
        self.items_on_screen = []
        self.spawn_phase_items() 

        # Carregamento e Redimensionamento das imagens dos inimigos
        self.enemy_images = {}
        try:
            # Substitua pelos nomes reais dos seus arquivos de imagem na pasta assets:
            self.enemy_images[1] = pygame.transform.scale(pygame.image.load("assets/inimigo_1955.png").convert_alpha(), (104, 130))
            self.enemy_images[2] = pygame.transform.scale(pygame.image.load("assets/inimigo_2015.png").convert_alpha(), (104, 130))
            self.enemy_images[3] = pygame.transform.scale(pygame.image.load("assets/inimigo_1885.png").convert_alpha(), (104, 130))
            print("🦹 Imagens dos inimigos carregadas com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao carregar imagens dos inimigos: {e}")

        # ESTADOS DO JOGO: "START", "PLAYING", "GAMEOVER", "WIN"
        self.game_state = "START" 
        
        # Carregar as imagens das telas (adicione na pasta assets)
        try:
            self.start_screen = pygame.transform.scale(pygame.image.load("assets/tela_inicial.png").convert(), (800, 600))
            self.game_over_screen = pygame.transform.scale(pygame.image.load("assets/tela_gameover.png").convert(), (800, 600))
            self.win_screen = pygame.transform.scale(pygame.image.load("assets/tela_vitoria.png").convert(), (800, 600))
            print("📺 Telas de menu carregadas com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao carregar telas de menu: {e}")

    def tocar_musica_fundo(self, caminho_arquivo):
        """Toca a música em loop, mas só carrega se for uma música diferente"""
        # Verifica se a música que pediu para tocar já é a que está rodando
        if pygame.mixer.music.get_busy():
            # Esse truque evita reiniciar a música se ela já for a mesma
            pass 
            
        pygame.mixer.music.stop()         # Para a música atual
        pygame.mixer.music.load(caminho_arquivo)
        pygame.mixer.music.set_volume(0.3) 
        pygame.mixer.music.play(-1)        # O argumento -1 faz tocar em loop infinito

    def spawn_phase_items(self):
        """Busca a imagem correta da fase e cria os itens colecionáveis na tela"""
        self.items_on_screen = []
        img_atual = self.item_images.get(self.current_level, self.item_images.get(1))
        
        if img_atual:
            # Passando a imagem direto na criação do objeto!
            item1 = Collectible(200, 470, img_atual)
            item2 = Collectible(350, 370, img_atual)
            item3 = Collectible(500, 470, img_atual)

            self.items_on_screen = [item1, item2, item3]

    def reset_game(self, game_over=False):
        """Reseta o estado para uma nova fase ou reinicia tudo em caso de Game Over"""
        if game_over:
            self.current_level = 1
            self.player = Player(20, 470)
            self.level_time = 60 
        else:
            self.player.x = 20
            self.player.y = 470
            self.player.rect.topleft = (20, 470)
            if self.current_level == 2:
                self.level_time = 30 
            elif self.current_level == 3:
                self.level_time = 999 

        self.enemies = []              
        self.shots = []                
        self.collected_items = 0       
        self.tower_spawned = False
        self.boss_spawned = False
        self.biff_escaped = False
        
        self.spawn_phase_items()
   
    def check_events(self):
        """Captura os eventos do teclado e do sistema"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            # 1. CONTROLES DOS MENUS (START, GAMEOVER, WIN)
            if event.type == pygame.KEYDOWN:
                # Se estiver na tela inicial e apertar ENTER, o jogo começa
                if self.game_state == "START" and event.key == pygame.K_RETURN:
                    self.game_state = "PLAYING"
                    self.tocar_musica_fundo(self.musica_jogo)
                    self.reset_game(game_over=True) # Começa do zero
                
                # Se deu Game Over ou Vitória e apertar ENTER, volta para o início
                elif (self.game_state == "GAMEOVER" or self.game_state == "WIN") and event.key == pygame.K_RETURN:
                    self.game_state = "START"
                        
            # 2. CONTROLES E EVENTOS DURANTE A PARTIDA
            if self.game_state == "PLAYING":
                # Temporizador do nível
                if event.type == self.time_event and self.current_level in [1, 2]:
                    self.level_time -= 1
                    if self.level_time <= 0:
                        self.game_state = "GAMEOVER"
                        self.tocar_musica_fundo(self.musica_gameover)

                # Spawn automático de inimigos
                if event.type == self.SPAWN_ENEMY_EVENT:
                    year_map = {1: 1955, 2: 2015, 3: 1885}
                    fase_ano = year_map.get(self.current_level, 1955)
                    img_atual = self.enemy_images.get(self.current_level, self.enemy_images.get(1))
                    
                    if fase_ano == 1885:
                        if not self.boss_spawned:
                            novo_boss = EnemyFactory.create_boss(750, 460, img_atual)
                            self.enemies.append(novo_boss)
                            self.boss_spawned = True
                    elif fase_ano == 2015:
                        if not self.boss_spawned:
                            biff_fugitivo = EnemyFactory.create_boss(800, 470, img_atual)
                            biff_fugitivo.speed = 2
                            self.enemies.append(biff_fugitivo)
                            self.boss_spawned = True
                    else:
                        novo_invertido = EnemyFactory.create_enemy(fase_ano, 850, 470, img_atual)
                        self.enemies.append(novo_invertido)

                # 🟢 CORRIGIDO: Captura de Pulo e Tiro perfeitamente alinhadas ao estado PLAYING
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.som_pulo.play() # 🔊 Toca o som do pulo imediatamente
                        keys = pygame.key.get_pressed()
                        direcao = 0
                        if keys[pygame.K_d]: direcao = 1   
                        if keys[pygame.K_a]: direcao = -1  

                        if self.current_level in [2, 3]:
                            self.player.jump(custom_jump_speed=-21, direction_x=direcao)
                        else:
                            self.player.jump(direction_x=direcao) 
                    
                    if event.key == pygame.K_SPACE:
                        self.som_tiro.play() # 🔊 Toca o som do tiro imediatamente
                        novo_tiro = self.player.shoot()
                        self.shots.append(novo_tiro)

    def update(self):
        """Atualiza a lógica interna e a física dos personagens"""
        if self.game_state != "PLAYING":
            return 
        
        self.player.update_physics()
        
        for enemy in self.enemies[:]:
            enemy.update_behavior()
            if self.current_level == 2 and enemy.x < 0:
                self.game_state = "GAMEOVER"
                return
        
        keys = pygame.key.get_pressed()
        esta_correndo = False
        
        if keys[pygame.K_a]: 
            self.player.move(-5, 0)
            esta_correndo = True
        if keys[pygame.K_d]: 
            self.player.move(5, 0)
            esta_correndo = True
            
        self.player.update_animation(self.current_level, esta_correndo)
        self.player.update_physics()
            
        self.enemies = [e for e in self.enemies if e.x > -50 or isinstance(e, Boss)]
        
        for shot in self.shots:
            shot.update_behavior()
        self.shots = [shot for shot in self.shots if shot.x < self.screen_width]

        # --- COLISÕES ---
        for shot in self.shots[:]:
            for enemy in self.enemies[:]:
                if shot.rect.colliderect(enemy.rect):
                    if shot in self.shots:
                        self.shots.remove(shot)

                    if isinstance(enemy, Boss):
                        if self.current_level == 2:
                            print("🛡️ O Biff está protegido!")
                        elif self.current_level == 3:
                            if self.collected_items < 3:
                                print("🛡️ Buford Tannen ri do seu tiro!")
                            else:
                                morreu = enemy.take_damage()
                                if morreu:
                                    if enemy in self.enemies:
                                        self.enemies.remove(enemy)
                                    self.player.score += 1000 
                                    self.tocar_musica_fundo(self.musica_vitoria)
                                    self.game_state = "WIN"
                    else:
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                        self.player.score += 100
                    break 

        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                if self.current_level == 2 and isinstance(enemy, Boss):
                    if self.collected_items < 3:
                        self.player.take_damage()
                        self.player.move(-40, 0) 
                    else:
                        self.current_level = 3
                        self.reset_game(game_over=False)
                        return 

                elif self.current_level == 3 and isinstance(enemy, Boss):
                    if self.collected_items < 3:
                        self.player.lives = 0 
                    else:
                        self.player.take_damage()
                        self.player.move(-50, 0) 
                else:
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.player.take_damage()
                
                if self.player.lives <= 0:
                    self.db.save_score("Marty McFly", self.player.score) 
                    self.reset_game(game_over=True)
                    self.game_state = "GAMEOVER"
                    return

        for item in self.items_on_screen[:]:
            if item.rect.colliderect(self.player.rect):
                self.items_on_screen.remove(item)
                self.collected_items += 1
                self.player.score += 200 

        if self.collected_items == 3:
            self.tower_spawned = True

        if self.tower_spawned and self.current_level == 1: 
            if self.player.rect.colliderect(self.clock_tower.rect):
                self.current_level = 2
                self.reset_game(game_over=False)

    def draw(self):
        """Renderiza os elementos gráficos na tela"""
        self.screen.fill((0, 0, 0))
        
        # 1. TELA INICIAL
        if self.game_state == "START":

            # Desenha a imagem de fundo primeiro
            self.screen.blit(self.start_screen, (0, 0))
            self.font.set_bold(True)
            title_text = self.title_font.render("", True, (255, 128, 0))
            instruct_text = self.font.render("Pressione [ENTER] para Iniciar o Jogo", True, (255, 255, 255))
            cmd_w = self.font.render("[W] - Pular", True, (255, 255, 255))
            cmd_ad = self.font.render("[A / D] - Mover para os Lados", True, (255, 255, 255))
            cmd_space = self.font.render("[ESPAÇO] - Atirar", True, (255, 255, 255))
            score_title = self.font.render("--- TOP RECORDES ---", True, (255, 255, 0))
            self.font.set_bold(False)

            self.screen.blit(title_text, (50, 80))
            self.screen.blit(instruct_text, (180, 180))
            self.screen.blit(cmd_w, (280, 260))
            self.screen.blit(cmd_ad, (280, 300))
            self.screen.blit(cmd_space, (280, 340))
            self.screen.blit(score_title, (270, 410))
            
            try:
                top_scores = self.db.get_top_scores(3)
                y_offset = 450
                for idx, row in enumerate(top_scores):
                    row_text = self.font.render(f"{idx+1}. {row[0]} - {row[1]} pts", True, (0, 255, 255))
                    self.screen.blit(row_text, (300, y_offset))
                    y_offset += 35
            except:
                pass
            
        # 2. TELA DE GAME OVER
        elif self.game_state == "GAMEOVER":
            # 🟢 CORRIGIDO: Desenha a imagem de game over primeiro
            self.screen.blit(self.game_over_screen, (0, 0))
            
            title_text = self.title_font.render("GAME OVER", True, (255, 0, 0))
            instruct_text = self.font.render("Pressione [ENTER] para Reiniciar", True, (255, 255, 255))
            self.screen.blit(title_text, (280, 200))
            self.screen.blit(instruct_text, (220, 300))

        # 3. TELA DE VITÓRIA
        elif self.game_state == "WIN":
            # 🟢 CORRIGIDO: Desenha a imagem de vitória primeiro
            self.screen.blit(self.win_screen, (0, 0))
            
            title_text = self.title_font.render("A linha do tempo foi salva!", True, (0, 255, 0))
            instruct_text = self.font.render("Pressione [ENTER] para Jogar de Novo", True, (255, 255, 255))
            self.screen.blit(title_text, (100, 200))
            self.screen.blit(instruct_text, (200, 300))
            
        # 4. DURANTE O JOGO (PLAYING)
        elif self.game_state == "PLAYING":
            if self.current_level in self.backgrounds:
                self.screen.blit(self.backgrounds[self.current_level], (0, 0))
            
            # ⚡ Efeito de Raio na Fase 1 (1955)
            if self.current_level == 1:
                import random
                # 1% de chance de soltar um relâmpago a cada frame
                if random.randint(1, 100) == 1:
                    # Cria uma superfície branca translúcida cobrindo a tela
                    raio = pygame.Surface((self.screen_width, self.screen_height))
                    raio.fill((255, 255, 255))
                    raio.set_alpha(150) # Transparência do flash
                    self.screen.blit(raio, (0, 0))

            for item in self.items_on_screen:
                item.draw(self.screen)
                
            if self.tower_spawned and self.current_level == 1:
                self.clock_tower.draw(self.screen)

            for enemy in self.enemies:
                enemy.draw(self.screen)
            for shot in self.shots:
                shot.draw(self.screen)
                
            self.player.draw(self.screen)
            
            # HUD
            score_display = self.font.render(f"Pontos: {self.player.score}", True, (255, 255, 255))
            lives_display = self.font.render(f"Vidas: {self.player.lives}", True, (255, 0, 0))
            self.screen.blit(score_display, (20, 20))
            self.screen.blit(lives_display, (650, 20))
            
            nome_item = {1: "Capacitores", 2: "Almanaques", 3: "Fotos"}
            hud_item = self.font.render(f"{nome_item[self.current_level]}: {self.collected_items}/3", True, (0, 255, 0))
            self.screen.blit(hud_item, (20, 60))
            
            if self.current_level in [1, 2]:
                time_display = self.font.render(f"Tempo: {self.level_time}s", True, (255, 255, 0))
                self.screen.blit(time_display, (350, 20))

    def run_game(self):
            """Loop principal modificado para gerenciar as telas"""
            while self.is_running:
                self.check_events()  # Continua lendo os comandos
                
                # Só atualiza a física e a lógica se o jogo estiver rolando!
                if self.game_state == "PLAYING":
                    self.update()        
                
                # Desenha a tela correta baseada no estado
                self.draw()          
                
                pygame.display.flip()
                self.clock.tick(60)
            
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    # Instancia o objeto do jogo e inicia o loop
    game = Game()
    game.run_game()