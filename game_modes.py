"""
Gestion des différents modes de jeu
"""
import pygame
from config import *

class GameModes:
    def __init__(self):
        self.available_modes = {
            "1v1": {
                "name": "Joueur vs Bot",
                "description": "Affrontez un bot dans 5 ou 10 manches",
                "players": 1,
                "rounds_options": [5, 10]
            },
            "2v1": {
                "name": "Deux joueurs vs Bot",
                "description": "Coopérez avec un ami contre le bot",
                "players": 2,
                "rounds_options": [5, 10]
            },
            "pvp": {
                "name": "Joueur vs Joueur",
                "description": "Affrontez-vous dans 10 manches",
                "players": 2,
                "rounds_options": [10]
            }
        }
        
        self.selected_mode = None
        self.selected_rounds = None
        self.bot_difficulty = "medium"  # "easy", "medium", "hard"
        
    def select_mode(self, mode, rounds, difficulty="medium"):
        """Sélectionne un mode de jeu"""
        if mode in self.available_modes:
            if rounds in self.available_modes[mode]["rounds_options"]:
                self.selected_mode = mode
                self.selected_rounds = rounds
                self.bot_difficulty = difficulty
                return True
        return False
    
    def get_mode_info(self, mode):
        """Récupère les informations d'un mode"""
        return self.available_modes.get(mode, None)
    
    def draw_mode_selection(self, screen, selected_index=0):
        """Dessine le menu de sélection de mode"""
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Titre
        title = font_large.render("Sélectionnez un mode de jeu", True, ORANGE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Liste des modes
        y_start = 200
        y_spacing = 120
        
        for i, (mode_key, mode_info) in enumerate(self.available_modes.items()):
            y = y_start + i * y_spacing
            
            # Fond si sélectionné
            if i == selected_index:
                highlight = pygame.Surface((SCREEN_WIDTH - 200, 100))
                highlight.set_alpha(100)
                highlight.fill(BLUE)
                screen.blit(highlight, (100, y - 10))
            
            # Nom du mode
            name_text = font_medium.render(mode_info["name"], True, WHITE)
            screen.blit(name_text, (150, y))
            
            # Description
            desc_text = font_small.render(mode_info["description"], True, GRAY)
            screen.blit(desc_text, (150, y + 35))
            
            # Options de manches
            rounds_text = font_small.render(
                f"Manches disponibles: {', '.join(map(str, mode_info['rounds_options']))}",
                True, YELLOW
            )
            screen.blit(rounds_text, (150, y + 60))
        
        # Instructions
        instruction = font_small.render(
            "Flèches ↑↓ pour naviguer | ESPACE pour sélectionner",
            True, WHITE
        )
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 100))

