"""
Classe des objets collectibles (Micro-puces)
"""
import pygame
import math
from config import *

class Collectible:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, COLLECTIBLE_SIZE, COLLECTIBLE_SIZE)
        self.collected = False
        self.color = YELLOW
        self.animation_offset = 0
        
    def update(self):
        """Met à jour l'animation"""
        if not self.collected:
            # Animation de rotation/flottement
            self.animation_offset += 0.1
    
    def check_collision(self, player):
        """Vérifie si le joueur a collecté l'objet"""
        if not self.collected and self.rect.colliderect(player.rect):
            self.collected = True
            return True
        return False
    
    def draw(self, screen):
        """Dessine un shuriken (étoile ninja) style pixel art"""
        if self.collected:
            return
        
        # Animation de flottement
        y_offset = int(3 * abs(math.sin(self.animation_offset)))
        
        center_x = self.rect.centerx
        center_y = self.rect.centery - y_offset
        
        # Dessiner un shuriken (étoile à 4 pointes)
        size = self.rect.width // 2
        # Rotation pour effet visuel
        rotation = self.animation_offset * 2
        
        # Points de l'étoile
        points = []
        for i in range(8):
            angle = (i * math.pi / 4) + rotation
            if i % 2 == 0:
                r = size
            else:
                r = size // 2
            px = center_x + r * math.cos(angle)
            py = center_y + r * math.sin(angle)
            points.append((px, py))
        
        # Dessiner le shuriken
        pygame.draw.polygon(screen, YELLOW, points)
        pygame.draw.polygon(screen, BLACK, points, 2)
        
        # Centre du shuriken
        pygame.draw.circle(screen, ORANGE, (int(center_x), int(center_y)), 3)
        pygame.draw.circle(screen, BLACK, (int(center_x), int(center_y)), 3, 1)

