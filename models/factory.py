import pygame
import random
from models.characters import Enemy
from models.characters import Enemy, Boss 

class EnemyFactory:
    @staticmethod
    def create_enemy(ano, x, y, imagem): # 👈 Adicione 'imagem' aqui
        # Seus ifs de comportamento por ano continuam aqui...
        if ano == 1955:
            return Enemy(x, y, imagem)  # 👈 Passa a imagem para o construtor do Enemy
        elif ano == 2015:
            return Enemy(x, y, imagem)
        elif ano == 1885:
            return Enemy(x, y, imagem)
            
        else:
            # Caso dê algum ano inválido, retorna um inimigo padrão
            return Enemy(x, y, speed=4)

    # Para a Fase 3, vamos criar um Boss especial! 
    @staticmethod
    def create_boss(x: int, y: int, imagem) -> Boss:
        """Cria o grande vilão Buford Tannen para a Fase 3"""
        return Boss(x, y, imagem)