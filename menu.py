"""
Gestion du menu principal
"""
import pygame
from config import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.selected_option = 0
        self.options = ["Jouer", "Nouvelle partie", "Mode Compétitif", "Scores", "Paramètres", "Quitter"]
        self.font_title = pygame.font.Font(None, 72)
        self.font_option = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
    
    def handle_event(self, event):
        """Gère les événements du menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected_option]
        return None
    
    def draw(self):
        """Dessine le menu avec fond coloré moderne"""
        # Fond dégradé violet/bleu nuit moderne
        from config import GRADIENT_START, GRADIENT_END
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Ajouter quelques nuages décoratifs
        for i in range(3):
            cloud_x = 100 + i * 400
            cloud_y = 100 + i * 50
            cloud_size = 40 + i * 10
            pygame.draw.circle(self.screen, CLOUD_WHITE, (cloud_x, cloud_y), cloud_size)
            pygame.draw.circle(self.screen, CLOUD_WHITE, (cloud_x + cloud_size // 2, cloud_y), cloud_size)
            pygame.draw.circle(self.screen, CLOUD_WHITE, (cloud_x - cloud_size // 2, cloud_y), cloud_size)
        
        # Titre avec ombre pour effet pixel art
        title = self.font_title.render("CYBER JUMP", True, ORANGE)
        title_shadow = self.font_title.render("CYBER JUMP", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + 3, 153))
        title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_shadow, title_shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.font_small.render("Plateformer 2D Fun & Coloré!", True, PURPLE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Options du menu avec couleurs vives
        y_offset = 350
        option_colors = [ORANGE, YELLOW, PURPLE, RED, CYAN, GRAY]  # Couleurs pour chaque option
        
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = option_colors[i % len(option_colors)]
                # Fond coloré pour l'option sélectionnée
                bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset + i * 80 - 25, 300, 50)
                pygame.draw.rect(self.screen, (color[0] // 4, color[1] // 4, color[2] // 4), bg_rect)
                pygame.draw.rect(self.screen, color, bg_rect, 3)
            else:
                color = GRAY
            
            text = self.font_option.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 80))
            self.screen.blit(text, text_rect)
            
            # Indicateur de sélection (flèche colorée)
            if i == self.selected_option:
                pygame.draw.polygon(self.screen, color, [
                    (text_rect.left - 30, text_rect.centery),
                    (text_rect.left - 10, text_rect.centery - 10),
                    (text_rect.left - 10, text_rect.centery + 10)
                ])

