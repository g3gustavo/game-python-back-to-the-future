import pygame
import random
from models.characters import Enemy

class EnemyFactory:
    @staticmethod
    def create_enemy(year: int, x: int, y: int) -> Enemy:
        """Padrão Factory - Centraliza a criação de inimigos baseado no Ano"""
        if year == 1955:
            # Capangas do Biff (Inimigo padrão, velocidade média)
            enemy = Enemy(x, y, speed=random.randint(3, 5))
            return enemy
            
        elif year == 2015:
            # Drones futuristas (Mais rápidos, voam um pouco mais alto)
            enemy = Enemy(x, y - random.randint(30, 80), speed=random.randint(6, 8))
            return enemy
            
        elif year == 1885:
            # Bandidos do Velho Oeste (Mais lentos, mas aguentam mais tranco no futuro)
            enemy = Enemy(x, y, speed=random.randint(2, 4))
            return enemy
            
        else:
            # Caso dê algum ano inválido, retorna um inimigo padrão
            return Enemy(x, y, speed=4)