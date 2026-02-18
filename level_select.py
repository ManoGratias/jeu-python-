"""
Menu de sélection de niveaux
"""
import pygame
from config import *

class LevelSelectMenu:
    def __init__(self, screen):
        self.screen = screen
        self.selected_level = 0
        self.levels = [
            {"name": "Parcours 1", "type": "parkour", "description": "Sauts et plateformes"},
            {"name": "1v1 Combat", "type": "1v1", "description": "Course contre un ennemi"},
            {"name": "Parcours 2", "type": "parkour", "description": "Défi de précision"}
        ]
        self.font_title = pygame.font.Font(None, 72)
        self.font_option = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
    
    def handle_event(self, event):
        """Gère les événements du menu de sélection"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_level = (self.selected_level - 1) % len(self.levels)
            elif event.key == pygame.K_DOWN:
                self.selected_level = (self.selected_level + 1) % len(self.levels)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.selected_level
            elif event.key == pygame.K_ESCAPE:
                return -1  # Retour au menu principal
        return None
    
    def handle_joystick_event(self, event):
        """Gère les événements de manette"""
        try:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Bouton X
                    return self.selected_level
                elif event.button == 9:  # Bouton Options
                    return -1
            
            elif event.type == pygame.JOYHATMOTION:
                if hasattr(event, 'joy') and event.joy < pygame.joystick.get_count():
                    hat = pygame.joystick.Joystick(event.joy).get_hat(0)
                    if hat[1] == 1:  # Haut
                        self.selected_level = (self.selected_level - 1) % len(self.levels)
                    elif hat[1] == -1:  # Bas
                        self.selected_level = (self.selected_level + 1) % len(self.levels)
        except:
            pass
        return None
    
    def draw(self):
        """Dessine le menu de sélection de niveaux"""
        # Fond
        self.screen.fill(SKY_BLUE)
        
        # Nuages décoratifs
        for i in range(3):
            cloud_x = 100 + i * 400
            cloud_y = 100 + i * 50
            cloud_size = 40 + i * 10
            pygame.draw.circle(self.screen, CLOUD_WHITE, (cloud_x, cloud_y), cloud_size)
            pygame.draw.circle(self.screen, CLOUD_WHITE, (cloud_x + cloud_size // 2, cloud_y), cloud_size)
            pygame.draw.circle(self.screen, CLOUD_WHITE, (cloud_x - cloud_size // 2, cloud_y), cloud_size)
        
        # Titre
        title = self.font_title.render("SÉLECTION DE NIVEAU", True, ORANGE)
        title_shadow = self.font_title.render("SÉLECTION DE NIVEAU", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + 3, 103))
        title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_shadow, title_shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Afficher les niveaux
        y_offset = 250
        level_colors = [ORANGE, RED, PURPLE]
        
        for i, level in enumerate(self.levels):
            is_selected = i == self.selected_level
            
            # Fond pour le niveau sélectionné
            if is_selected:
                color = level_colors[i]
                bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, y_offset + i * 120 - 30, 400, 80)
                pygame.draw.rect(self.screen, (color[0] // 4, color[1] // 4, color[2] // 4), bg_rect)
                pygame.draw.rect(self.screen, color, bg_rect, 4)
            else:
                color = GRAY
            
            # Nom du niveau
            name_text = self.font_option.render(level["name"], True, color)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 120))
            self.screen.blit(name_text, name_rect)
            
            # Description
            desc_text = self.font_small.render(level["description"], True, color)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 120 + 35))
            self.screen.blit(desc_text, desc_rect)
            
            # Type de niveau (badge)
            type_color = GREEN if level["type"] == "parkour" else RED
            type_text = self.font_small.render(level["type"].upper(), True, type_color)
            type_rect = type_text.get_rect(center=(SCREEN_WIDTH // 2 + 150, y_offset + i * 120))
            pygame.draw.rect(self.screen, type_color, 
                           (type_rect.left - 5, type_rect.top - 2, type_rect.width + 10, type_rect.height + 4), 2)
            self.screen.blit(type_text, type_rect)
            
            # Flèche de sélection
            if is_selected:
                pygame.draw.polygon(self.screen, color, [
                    (name_rect.left - 30, name_rect.centery),
                    (name_rect.left - 10, name_rect.centery - 10),
                    (name_rect.left - 10, name_rect.centery + 10)
                ])
        
        # Instructions
        instructions = [
            "Flèches ↑↓ : Naviguer | Entrée : Sélectionner | ESC : Retour"
        ]
        y_inst = SCREEN_HEIGHT - 80
        for i, inst in enumerate(instructions):
            text = self.font_small.render(inst, True, GRAY)
            self.screen.blit(text, (50, y_inst + i * 30))

