"""
Classe des plateformes
"""
import pygame
from config import *

class Platform:
    def __init__(self, x, y, width):
        self.rect = pygame.Rect(x, y, width, PLATFORM_HEIGHT)
        
    def draw(self, screen):
        """Dessine la plateforme style pixel art orange/vert"""
        # Corps principal orange
        pygame.draw.rect(screen, ORANGE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Sommet vert (comme dans l'image)
        top_height = 4
        top_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, top_height)
        pygame.draw.rect(screen, PLATFORM_GREEN, top_rect)
        pygame.draw.rect(screen, BLACK, top_rect, 1)
        
        # Détails pixel art (petits carrés pour texture)
        for i in range(0, self.rect.width, 8):
            if i % 16 == 0:
                detail_rect = pygame.Rect(self.rect.x + i, self.rect.y + top_height + 2, 4, 2)
                pygame.draw.rect(screen, (200, 100, 0), detail_rect)

