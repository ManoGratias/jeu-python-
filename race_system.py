"""
Système de course chronométré
"""
import pygame
from config import *

class RaceSystem:
    def __init__(self):
        self.race_started = False
        self.race_finished = False
        self.start_time = 0
        self.finish_time = 0
        self.current_time = 0
        
        # Temps des joueurs
        self.player1_time = 0
        self.player2_time = 0
        self.bot_time = 0
        
    def start_race(self):
        """Démarre la course"""
        self.race_started = True
        self.race_finished = False
        self.start_time = pygame.time.get_ticks() / 1000  # Temps en secondes
        self.current_time = 0
        self.player1_time = 0
        self.player2_time = 0
        self.bot_time = 0
    
    def update(self):
        """Met à jour le chronomètre"""
        if self.race_started and not self.race_finished:
            self.current_time = (pygame.time.get_ticks() / 1000) - self.start_time
    
    def finish_race(self, player_id="player1"):
        """Termine la course pour un joueur"""
        if not self.race_finished:
            if player_id == "player1":
                self.player1_time = self.current_time
            elif player_id == "player2":
                self.player2_time = self.current_time
        
        # La course est terminée quand tous les joueurs ont fini
        # (ou quand le joueur principal finit en mode 1v1)
    
    def get_time_string(self, time_seconds):
        """Convertit le temps en chaîne formatée MM:SS.mmm"""
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        milliseconds = int((time_seconds % 1) * 1000)
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    def draw_timer(self, screen, x, y, color=WHITE):
        """Dessine le chronomètre"""
        font = pygame.font.Font(None, 48)
        time_str = self.get_time_string(self.current_time)
        text = font.render(time_str, True, color)
        screen.blit(text, (x, y))
        return text.get_width()
    
    def draw_race_hud(self, screen, match_manager):
        """Dessine l'interface de course"""
        font = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Titre de la manche
        round_text = font.render(
            f"Manche {match_manager.current_round}/{match_manager.num_rounds}",
            True, WHITE
        )
        screen.blit(round_text, (20, 20))
        
        # Chronomètre principal
        timer_y = 60
        timer_label = font_small.render("Temps:", True, WHITE)
        screen.blit(timer_label, (20, timer_y))
        self.draw_timer(screen, 20, timer_y + 30, YELLOW)
        
        # Scores des manches précédentes
        y_offset = 150
        scores_text = font_small.render("Score des manches:", True, WHITE)
        screen.blit(scores_text, (20, y_offset))
        
        y_offset += 30
        p1_score = font_small.render(
            f"Joueur 1: {match_manager.player1_wins} victoires",
            True, BLUE
        )
        screen.blit(p1_score, (20, y_offset))
        
        if match_manager.game_mode == "pvp":
            y_offset += 25
            p2_score = font_small.render(
                f"Joueur 2: {match_manager.player2_wins} victoires",
                True, GREEN
            )
            screen.blit(p2_score, (20, y_offset))
        elif match_manager.game_mode in ["1v1", "2v1"]:
            y_offset += 25
            bot_score = font_small.render(
                f"Bot: {match_manager.bot_wins} victoires",
                True, RED
            )
            screen.blit(bot_score, (20, y_offset))
        
        # Instructions
        if not self.race_finished:
            instruction = font_small.render(
                "Allez jusqu'au drapeau pour terminer la course!",
                True, YELLOW
            )
            screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 50))

