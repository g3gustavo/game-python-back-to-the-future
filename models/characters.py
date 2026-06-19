import pygame
from models.entity import Entity
from models.projectile import Shot

class Player(Entity):
    def __init__(self, x: int, y: int):
        # Inicializa a classe mãe com uma imagem padrão de segurança
        super().__init__(x, y, image_path=None)
        
        self.lives = 3
        self.score = 0
        self.is_jumping = False
        self.jump_speed = -15
        self.gravity = 1
        self.velocity_y = 0

        # 🔫 Novo controle para saber se ele está atirando (para mudar o boneco)
        self.shoot_cooldown = 0 

        # 👕 DICIONÁRIO DE ROUPAS E ESTADOS (12 Bonecos)
        self.sprites = {1: {}, 2: {}, 3: {}}
        self.load_costumes()

        # Define o rect inicial baseado no tamanho já redimensionado
        self.image = self.sprites[1]["idle"]
        self.rect = self.image.get_rect() # 👈 Isso pega automaticamente a largura/altura novas!
        self.rect.topleft = (x, y)

    def load_costumes(self):
            """Carrega os 12 bonecos mantendo a proporção original com altura fixa de 83px"""
            acoes = ["idle", "run", "jump", "shoot"]
            
            # 📐 Definimos apenas a ALTURA que você quer fixar no jogo
            altura_desejada = 120 

            for fase in [1, 2, 3]:
                for acao in acoes:
                    caminho = f"assets/player_f{fase}_{acao}.png"
                    try:
                        # 1. Carrega a imagem original com o tamanho original dela
                        imagem_original = pygame.image.load(caminho).convert_alpha()
                        largura_original = imagem_original.get_width()
                        altura_original = imagem_original.get_height()
                        
                        # 2. 🧮 Calcula a proporção: quanto a imagem original precisa encolher ou esticar?
                        proporcao = altura_desejada / altura_original
                        
                        # 3. Define a nova largura baseada na proporção daquela imagem específica
                        nova_largura = int(largura_original * proporcao)
                        novo_tamanho = (nova_largura, altura_desejada)
                        
                        # 4. Redimensiona perfeitamente sem distorcer!
                        self.sprites[fase][acao] = pygame.transform.scale(imagem_original, novo_tamanho)
                        
                    except Exception as e:
                        print(f"⚠️ Não achei o boneco: {caminho}. Usando bloco reserva.")
                        # Fallback caso a imagem não exista (usa uma largura padrão de 60px)
                        superficie_reserva = pygame.Surface((60, altura_desejada))
                        cores = {1: (220, 20, 60), 2: (30, 144, 255), 3: (218, 165, 32)}
                        superficie_reserva.fill(cores[fase])
                        self.sprites[fase][acao] = superficie_reserva

    def update_animation(self, current_level: int, mudou_eixo_x: bool):
        """Escolhe o boneco correto baseado na fase e no que o Marty está fazendo"""
        
        # Reduz o tempo do sprite de tiro para ele voltar a andar/ficar parado
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # 1. Prioridade máxima: Ele está atirando?
        if self.shoot_cooldown > 0:
            self.image = self.sprites[current_level]["shoot"]
        
        # 2. Segunda prioridade: Ele está no ar pulando?
        elif self.is_jumping:
            self.image = self.sprites[current_level]["jump"]
        
        # 3. Terceira prioridade: Ele está se movimentando para os lados?
        elif mudou_eixo_x:
            self.image = self.sprites[current_level]["run"]
        
        # 4. Caso contrário: Está parado!
        else:
            self.image = self.sprites[current_level]["idle"]

        # Atualiza o tamanho do rect para a largura exata do sprite atualizado!
        posicao_atual = self.rect.topleft # Salva onde ele estava para não brotar em outro lugar
        self.rect = self.image.get_rect()
        self.rect.topleft = posicao_atual # Devolve o Marty para a posição certa

    def jump(self, custom_jump_speed: int = None, direction_x: int = 0):
        """Lógica do pulo com impulso horizontal"""
        if not self.is_jumping:
            self.is_jumping = True
            
            if custom_jump_speed is not None:
                self.velocity_y = custom_jump_speed
            else:
                self.velocity_y = self.jump_speed

            if custom_jump_speed is not None: 
                self.velocity_x = direction_x * 8  
            else:
                self.velocity_x = direction_x * 4  

    def update_physics(self):
        """Aplica gravidade e inércia horizontal ao pulo"""
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            self.x += self.velocity_x
            
            if self.y >= 470: 
                self.y = 470
                self.is_jumping = False
                self.velocity_y = 0
                self.velocity_x = 0
        
        # Limita o Marty dentro das bordas da tela
        # Impede de sair pela esquerda (X menor que 0)
        if self.x < 0:
            self.x = 0
            
        # Impede de sair pela direita (X maior que a largura da tela menos o tamanho dele)
        # Se a sua tela tiver 800 de largura e o Marty tiver 50 de largura:
        if self.x > 750: 
            self.x = 750

        # Atualiza a posição visual na tela
        self.rect.topleft = (self.x, self.y)

    def shoot(self):
        """Instancia um tiro e ativa o sprite de ataque por alguns frames"""
        self.shoot_cooldown = 10 # Mantém o boneco atirando por 10 frames (~0.15 segundos)
        tiro = Shot(self.rect.right, self.rect.centery - 2)
        return tiro

    def take_damage(self):
        self.lives -= 1

class Enemy(Entity):
    def __init__(self, x: int, y: int, image, speed: int = 5):
        
        super().__init__(x, y, image_path=None) 
        
        self.image = image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
        self.speed = speed

    def update_behavior(self):
        """Faz o inimigo andar automaticamente para a esquerda"""
        self.move(-self.speed, 0)

class Boss(Enemy):
    def __init__(self, x: int, y: int, image):
        # O Boss começa com velocidade 3, mas vamos carregar o sprite dele do Velho Oeste
        super().__init__(x, y, image, speed=3)
        self.hp = 5 # O Boss precisa levar 5 tiros para morrer!

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
    
