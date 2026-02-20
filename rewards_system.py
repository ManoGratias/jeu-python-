"""
Système de récompenses - Affiche et gère les récompenses après chaque course
"""
import pygame
import random
from config import *

class RewardsSystem:
    def __init__(self, match_manager, on_transition_to_combat=None):
        self.match_manager = match_manager
        self.on_transition_to_combat = on_transition_to_combat
        self.showing_rewards = False
        self.display_timer = 0
        self.display_duration = 3
        self.victory_particles = []
        
    def show_rewards(self):
        """Affiche les récompenses (animation victoire UNIQUEMENT après manche 5)"""
        self.showing_rewards = True
        self.display_timer = 0
        if self.match_manager.current_round == self.match_manager.num_rounds:
            self._create_confetti()
        
    def _create_confetti(self):
        """Crée des particules de confetti pour l'animation victoire"""
        self.victory_particles = []
        colors = [YELLOW, ORANGE, GREEN, BLUE, PINK, RED, PURPLE]
        for _ in range(80):
            self.victory_particles.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(-SCREEN_HEIGHT, 0),
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(2, 8),
                "size": random.randint(4, 12),
                "color": random.choice(colors),
                "rot": random.uniform(0, 360),
                "rot_speed": random.uniform(-15, 15),
            })
        
    def update(self):
        """Met à jour l'affichage des récompenses"""
        if self.showing_rewards:
            self.display_timer += 1/60
            # Mettre à jour les particules de confetti (manche 5 uniquement)
            if self.match_manager.current_round == self.match_manager.num_rounds:
                for p in self.victory_particles:
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vy"] += 0.15
                    p["rot"] += p["rot_speed"]
            
            if self.display_timer >= self.display_duration:
                # Si manche 4, passer directement à la manche 5 (round_intro)
                if self.match_manager.current_round == 4:
                    # FORCER la transition vers la manche 5
                    print(f"[DEBUG] Transition manche 4 -> 5: current_round={self.match_manager.current_round}")
                    # Changer round_state AVANT current_round pour forcer la transition
                    self.match_manager.round_state = "round_intro"
                    self.match_manager.current_round = 5
                    self.match_manager.race_completed = False
                    self.match_manager.rewards_shown = False
                    self.match_manager.combat_completed = False
                    self.match_manager.current_rewards = {
                        "player1": {"coins": 0, "items": []},
                        "player2": {"coins": 0, "items": []} if self.match_manager.game_mode in ["2v1", "pvp"] else None
                    }
                    self.showing_rewards = False  # Mettre à False APRÈS avoir changé round_state
                    print(f"[DEBUG] Après transition: current_round={self.match_manager.current_round}, round_state={self.match_manager.round_state}")
                    # IMPORTANT: Le round_intro sera géré dans update_competitive dans le même frame
                    # car on utilise "if" au lieu de "elif" pour le bloc round_intro
                else:
                    self.showing_rewards = False
                    # Pour les autres manches, appeler show_rewards() pour déterminer le mini-jeu
                    self.match_manager.show_rewards()
                    # Si on passe directement à la manche 5 (round_state = "round_intro"), ne pas appeler la transition
                    if self.match_manager.round_state != "round_intro":
                        if self.on_transition_to_combat:
                            self.on_transition_to_combat()
    
    def draw(self, screen):
        """Dessine l'écran de récompenses (victoire UNIQUEMENT manche 5)"""
        if not self.showing_rewards:
            return
        
        # Fond : dégradé violet (manches 1-4) ou overlay sombre (manche 5 avec confettis)
        is_last_round = self.match_manager.current_round == self.match_manager.num_rounds
        if is_last_round:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
        else:
            from config import GRADIENT_START, GRADIENT_END
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
                g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
                b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
                screen.fill((r, g, b), (0, y, SCREEN_WIDTH, 1))
        
        # Animation victoire : confetti + "VOUS AVEZ GAGNÉ!" UNIQUEMENT après manche 5
        is_last_round = self.match_manager.current_round == self.match_manager.num_rounds
        if is_last_round and self.display_timer < 2.5:
            for p in self.victory_particles:
                if p["y"] < SCREEN_HEIGHT + 20:
                    s = pygame.Surface((p["size"], p["size"]))
                    s.fill(p["color"])
                    s.set_alpha(230)
                    rect = s.get_rect(center=(int(p["x"]), int(p["y"])))
                    screen.blit(s, rect)
            
            # "VOUS AVEZ GAGNÉ!" avec effet bounce/zoom
            bounce = abs(((self.display_timer * 4) % 2) - 1) * 8 + 1
            font_size = int(48 + 20 * bounce)
            font_victory = pygame.font.Font(None, font_size)
            victory_text = font_victory.render("🎉 VOUS AVEZ GAGNÉ ! 🎉", True, YELLOW)
            victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
            # Ombre
            shadow = font_victory.render("🎉 VOUS AVEZ GAGNÉ ! 🎉", True, BLACK)
            screen.blit(shadow, (victory_rect.x + 3, victory_rect.y + 3))
            screen.blit(victory_text, victory_rect)
            # Sous-titre animé
            sub = pygame.font.Font(None, 28).render("Course terminée !", True, GREEN)
            screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 170))
        
        # Titre récompenses (position selon si victoire affichée)
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("🎁 RÉCOMPENSES 🎁", True, YELLOW)
        title_y = 100 if (not is_last_round or self.display_timer >= 2.5) else 220
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, title_y))
        
        # Informations de la manche
        font_medium = pygame.font.Font(None, 32)
        round_text = font_medium.render(
            f"Manche {self.match_manager.current_round}/{self.match_manager.num_rounds}",
            True, WHITE
        )
        round_y = 260 if (not is_last_round or self.display_timer >= 2.5) else 250
        screen.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, round_y))
        
        # Récompenses du joueur 1
        y_start = 320 if (not is_last_round or self.display_timer >= 2.5) else 300
        self._draw_player_rewards(screen, "Joueur 1", 
                                 self.match_manager.current_rewards["player1"],
                                 SCREEN_WIDTH // 2 - 200, y_start, BLUE)
        
        # Récompenses du joueur 2 (si présent)
        if self.match_manager.game_mode in ["2v1", "pvp"]:
            self._draw_player_rewards(screen, "Joueur 2",
                                     self.match_manager.current_rewards["player2"],
                                     SCREEN_WIDTH // 2 + 200, y_start, GREEN)
        
        # Instructions (manche 5 = pas de combat)
        font_small = pygame.font.Font(None, 24)
        if is_last_round:
            instruction = font_small.render("Match terminé ! Bravo !", True, GREEN)
            hint = font_small.render("Espace/Entrée : Résultats  |  ESC : Menu", True, GRAY)
        else:
            instruction = font_small.render("Préparez-vous pour le combat!", True, WHITE)
            hint = font_small.render("Espace/Entrée : Combat  |  ESC : Retour au menu", True, GRAY)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 120))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 70))
    
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

