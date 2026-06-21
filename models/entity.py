import pygame
import os
import sys

def obter_caminho_recurso(caminho_relativo):
    """ Retorna o caminho absoluto para o recurso usando o padrão oficial do PyInstaller """
    try:
        # Se for o executável, ele extrai tudo para o _MEIPASS (que já mapeia o _internal automaticamente no Python 3)
        base_path = sys._MEIPASS
    except Exception:
        # Se for o VS Code, roda na raiz atual
        base_path = os.path.abspath(".")
    
    caminho_limpo = caminho_relativo.lstrip("./").lstrip("../")
    return os.path.join(base_path, caminho_limpo)

class Entity:
    def __init__(self, x: int, y: int, image_path: str = None):
        self.x = x
        self.y = y
        
        if image_path:
            # 🟢 Aplica a função para blindar o caminho da imagem
            caminho_final = obter_caminho_recurso(image_path)
            try:
                self.image = pygame.image.load(caminho_final).convert_alpha()
            except Exception as e:
                print(f"⚠️ Alerta: Não foi possível carregar {caminho_final}. Criando bloco reserva.")
                self.image = pygame.Surface((50, 50))
                self.image.fill((255, 0, 0)) # Quadrado vermelho de segurança para o jogo não fechar
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 255, 255))
            
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