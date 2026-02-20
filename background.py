"""
Gestion du fond avec nuages et ciel
"""
import pygame
import random
from config import *

class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.2, 0.5)
        self.size = random.randint(30, 60)
    
    def update(self):
        """Met à jour la position du nuage"""
        self.x += self.speed
        if self.x > SCREEN_WIDTH + 100:
            self.x = -100
    
    def draw(self, screen):
        """Dessine un nuage style pixel art"""
        # Nuage fait de plusieurs cercles
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x), int(self.y)), self.size // 2)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x + self.size // 3), int(self.y)), self.size // 2)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x - self.size // 3), int(self.y)), self.size // 2)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x), int(self.y - self.size // 4)), self.size // 2)
        
        # Contour noir pour style pixel art
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size // 2, 1)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.size // 3), int(self.y)), self.size // 2, 1)
        pygame.draw.circle(screen, BLACK, (int(self.x - self.size // 3), int(self.y)), self.size // 2, 1)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y - self.size // 4)), self.size // 2, 1)

class Background:
    def __init__(self):
        self.clouds = []
        # Créer quelques nuages aléatoires
        for _ in range(5):
            x = random.randint(-100, SCREEN_WIDTH + 100)
            y = random.randint(50, SCREEN_HEIGHT // 3)
            self.clouds.append(Cloud(x, y))
    
    def update(self):
        """Met à jour tous les nuages"""
        for cloud in self.clouds:
            cloud.update()
    
    def draw(self, screen):
        """Dessine le fond avec dégradé violet/bleu nuit et nuages"""
        # Fond dégradé violet/bleu nuit moderne
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))
        
        # Dessiner les nuages
        for cloud in self.clouds:
            cloud.draw(screen)

