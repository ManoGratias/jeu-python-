"""
Système de récompenses - Affiche et gère les récompenses après chaque course
"""
import pygame
from config import *

class RewardsSystem:
    def __init__(self, match_manager):
        self.match_manager = match_manager
        self.showing_rewards = False
        self.display_timer = 0
        self.display_duration = 3  # Afficher pendant 3 secondes
        
    def show_rewards(self):
        """Affiche les récompenses"""
        self.showing_rewards = True
        self.display_timer = 0
        
    def update(self):
        """Met à jour l'affichage des récompenses"""
        if self.showing_rewards:
            self.display_timer += 1/60  # 60 FPS
            
            if self.display_timer >= self.display_duration:
                self.showing_rewards = False
                self.match_manager.show_rewards()
    
    def draw(self, screen):
        """Dessine l'écran de récompenses"""
        if not self.showing_rewards:
            return
        
        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Titre
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("🎁 RÉCOMPENSES 🎁", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Informations de la manche
        font_medium = pygame.font.Font(None, 32)
        round_text = font_medium.render(
            f"Manche {self.match_manager.current_round}/{self.match_manager.num_rounds}",
            True, WHITE
        )
        screen.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, 180))
        
        # Récompenses du joueur 1
        y_start = 250
        self._draw_player_rewards(screen, "Joueur 1", 
                                 self.match_manager.current_rewards["player1"],
                                 SCREEN_WIDTH // 2 - 200, y_start, BLUE)
        
        # Récompenses du joueur 2 (si présent)
        if self.match_manager.game_mode in ["2v1", "pvp"]:
            self._draw_player_rewards(screen, "Joueur 2",
                                     self.match_manager.current_rewards["player2"],
                                     SCREEN_WIDTH // 2 + 200, y_start, GREEN)
        
        # Instructions
        font_small = pygame.font.Font(None, 24)
        instruction = font_small.render("Préparez-vous pour le combat!", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def _draw_player_rewards(self, screen, player_name, rewards, x, y, color):
        """Dessine les récompenses d'un joueur"""
        font = pygame.font.Font(None, 28)
        
        # Nom du joueur
        name_text = font.render(player_name, True, color)
        screen.blit(name_text, (x - name_text.get_width() // 2, y))
        
        # Pièces
        y += 50
        coins_text = font.render(f"💰 {rewards['coins']} pièces", True, YELLOW)
        screen.blit(coins_text, (x - coins_text.get_width() // 2, y))
        
        # Items
        y += 50
        if rewards['items']:
            items_label = font.render("Items obtenus:", True, WHITE)
            screen.blit(items_label, (x - items_label.get_width() // 2, y))
            y += 35
            
            item_names = {
                "speed_boost": "⚡ Boost de vitesse",
                "shield": "🛡️ Bouclier",
                "double_jump": "🦘 Double saut",
                "slow_time": "⏱️ Ralentissement"
            }
            
            for item in rewards['items']:
                item_text = font.render(item_names.get(item, item), True, GREEN)
                screen.blit(item_text, (x - item_text.get_width() // 2, y))
                y += 30
        else:
            no_items = font.render("Aucun item", True, GRAY)
            screen.blit(no_items, (x - no_items.get_width() // 2, y))

