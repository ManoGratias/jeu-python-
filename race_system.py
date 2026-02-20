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
        self.player1_finished = False
        self.player2_finished = False
        
    def start_race(self):
        """Démarre la course"""
        self.race_started = True
        self.race_finished = False
        self.start_time = pygame.time.get_ticks() / 1000  # Temps en secondes
        self.current_time = 0
        self.player1_time = 0
        self.player2_time = 0
        self.bot_time = 0
        self.player1_finished = False
        self.player2_finished = False
    
    def update(self):
        """Met à jour le chronomètre"""
        if self.race_started and not self.race_finished:
            self.current_time = (pygame.time.get_ticks() / 1000) - self.start_time
    
    def finish_race(self, player_id="player1"):
        """Termine la course pour un joueur"""
        if player_id == "player1" and not self.player1_finished:
            self.player1_time = self.current_time
            self.player1_finished = True
        elif player_id == "player2" and not self.player2_finished:
            self.player2_time = self.current_time
            self.player2_finished = True
    
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
    
    def draw_race_hud(self, screen, match_manager, player=None, level=None):
        """Dessine l'interface de course"""
        font = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Titre de la manche et niveau
        level_id = min(match_manager.current_round - 1, 4)
        niveau_nom = "Boss" if level_id == 4 else f"Niveau {level_id + 1}"
        round_text = font.render(
            f"Manche {match_manager.current_round}/{match_manager.num_rounds}  —  {niveau_nom}",
            True, WHITE
        )
        screen.blit(round_text, (20, 20))
        
        # Timer boss (3min15 max) - afficher le temps restant (seulement si le timer a démarré)
        if level and level.level_type == "boss" and hasattr(level, 'boss_start_time') and level.boss_start_time is not None:
            # Vérifier si le boss explose (victoire)
            if level.boss and level.boss.exploding:
                # Message de victoire quand le boss explose avec le score
                victory_font = pygame.font.Font(None, 56)
                score_font = pygame.font.Font(None, 36)
                victory_text = victory_font.render("🎉 VOUS AVEZ GAGNÉ ! 🎉", True, YELLOW)
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
                
                # Afficher le score
                if match_manager.game_mode == "1v1":
                    score_text = score_font.render(
                        f"Score Final: Joueur 1: {match_manager.player1_score} pts | Bot: {match_manager.bot_score} pts",
                        True, WHITE
                    )
                elif match_manager.game_mode == "pvp":
                    score_text = score_font.render(
                        f"Score Final: Joueur 1: {match_manager.player1_score} pts | Joueur 2: {match_manager.player2_score} pts",
                        True, WHITE
                    )
                elif match_manager.game_mode == "2v1":
                    score_text = score_font.render(
                        f"Score Final: J1: {match_manager.player1_score} pts | J2: {match_manager.player2_score} pts | Bot: {match_manager.bot_score} pts",
                        True, WHITE
                    )
                else:
                    score_text = score_font.render(
                        f"Score Final: {match_manager.player1_score} pts",
                        True, WHITE
                    )
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
                
                # Fond semi-transparent
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                screen.blit(overlay, (0, 0))
                screen.blit(victory_text, victory_rect)
                screen.blit(score_text, score_rect)
            else:
                elapsed_ms = pygame.time.get_ticks() - level.boss_start_time
                elapsed_seconds = elapsed_ms / 1000.0
                remaining_seconds = max(0, 195 - elapsed_seconds)  # 3min15 = 195 secondes
                minutes = int(remaining_seconds // 60)
                seconds = int(remaining_seconds % 60)
                timer_boss_text = font_small.render(
                    f"⏱ Temps restant: {minutes:02d}:{seconds:02d}",
                    True, RED if remaining_seconds < 30 else YELLOW
                )
            screen.blit(timer_boss_text, (SCREEN_WIDTH - 250, 20))
        
        # Indicateur du bonus de saut (étoiles bleues)
        if player and getattr(player, 'jump_bonus_timer', 0) > 0:
            bonus_seconds = int(player.jump_bonus_timer / 60) + 1
            bonus_text = font_small.render(
                f"⭐ Bonus Saut Actif: {bonus_seconds}s - Tuez les ennemis en l'air!",
                True, CYAN
            )
            screen.blit(bonus_text, (20, SCREEN_HEIGHT - 40))
        
        # Chronomètre principal
        timer_y = 60
        timer_label = font_small.render("Temps:", True, WHITE)
        screen.blit(timer_label, (20, timer_y))
        self.draw_timer(screen, 20, timer_y + 30, YELLOW)
        
        # Points (course + combat)
        y_offset = 150
        scores_text = font_small.render("Points (course 1pt + mini-jeu 5pts):", True, WHITE)
        screen.blit(scores_text, (20, y_offset))
        
        y_offset += 30
        p1_score = font_small.render(
            f"Joueur 1: {match_manager.player1_score} pts",
            True, BLUE
        )
        screen.blit(p1_score, (20, y_offset))
        
        if match_manager.game_mode == "pvp":
            y_offset += 25
            p2_score = font_small.render(
                f"Joueur 2: {match_manager.player2_score} pts",
                True, GREEN
            )
            screen.blit(p2_score, (20, y_offset))
        elif match_manager.game_mode == "2v1":
            y_offset += 25
            p2_score = font_small.render(
                f"Joueur 2: {match_manager.player2_score} pts",
                True, GREEN
            )
            screen.blit(p2_score, (20, y_offset))
            y_offset += 25
            bot_score = font_small.render(
                f"Bot: {match_manager.bot_score} pts",
                True, RED
            )
            screen.blit(bot_score, (20, y_offset))
        elif match_manager.game_mode == "1v1":
            y_offset += 25
            bot_score = font_small.render(
                f"Bot: {match_manager.bot_score} pts",
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

