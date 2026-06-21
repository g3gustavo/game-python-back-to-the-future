import pygame
import os
import sys
from models.characters import Enemy, Boss 

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

class EnemyFactory:
    @staticmethod
    def create_enemy(ano, x, y, imagem):
        # 🟢 Se 'imagem' for o texto do caminho (string), nós a carregamos com segurança aqui dentro
        if isinstance(imagem, str):
            caminho_seguro = obter_caminho_recurso(imagem)
            try:
                imagem_carregada = pygame.image.load(caminho_seguro).convert_alpha()
            except Exception as e:
                print(f"⚠️ Alerta: Não foi possível carregar {caminho_seguro}. Usando imagem reserva.")
                # Cria um quadrado vermelho temporário para o jogo não quebrar se o arquivo sumir
                imagem_carregada = pygame.Surface((50, 50))
                imagem_carregada.fill((255, 0, 0))
            imagem = imagem_carregada

        return Enemy(x, y, imagem)

    @staticmethod
    def create_boss(x: int, y: int, imagem) -> Boss:
        # 🟢 Faz o mesmo tratamento de segurança para o Chefe Final
        if isinstance(imagem, str):
            caminho_seguro = obter_caminho_recurso(imagem)
            try:
                imagem_carregada = pygame.image.load(caminho_seguro).convert_alpha()
            except Exception as e:
                print(f"⚠️ Alerta Boss: Não foi possível carregar {caminho_seguro}.")
                imagem_carregada = pygame.Surface((70, 120))
                imagem_carregada.fill((139, 0, 0))
            imagem = imagem_carregada

        return Boss(x, y, imagem)