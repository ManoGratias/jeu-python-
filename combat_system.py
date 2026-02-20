"""
Système de combat - Gère les combats après chaque course
"""
import pygame
import random
from config import *

class CombatSystem:
    def __init__(self, match_manager):
        self.match_manager = match_manager
        self.combat_active = False
        self.combat_timer = 0
        self.max_combat_time = 30  # 30 secondes par combat
        
        # Stats des combattants
        self.player1_health = 100
        self.player2_health = 100
        self.bot_health = 100
        
        self.player1_max_health = 100
        self.player2_max_health = 100
        self.bot_max_health = 100
        
        # Positions pour le combat
        self.player1_pos = [200, SCREEN_HEIGHT - 150]
        self.player2_pos = [400, SCREEN_HEIGHT - 150]
        self.bot_pos = [800, SCREEN_HEIGHT - 150]
        
        # État des attaques
        self.player1_attacking = False
        self.player2_attacking = False
        self.bot_attacking = False
        self.attack_timer = 0
        
        # Items actifs
        self.player1_items = []
        self.player2_items = []
        self.bot_items = []
        
    def start_combat(self, player1_items=None, player2_items=None):
        """Démarre un nouveau combat"""
        self.combat_active = True
        self.combat_timer = 0
        
        # Réinitialiser les stats
        self.player1_health = self.player1_max_health
        self.player2_health = self.player2_max_health
        self.bot_health = self.bot_max_health
        
        # Appliquer les items
        self.player1_items = player1_items or []
        self.player2_items = player2_items or []
        
        # Appliquer les effets des items
        self._apply_items()
        
    def _apply_items(self):
        """Applique les effets des items"""
        # Shield : +20 HP
        if "shield" in self.player1_items:
            self.player1_max_health = 120
            self.player1_health = 120
        if "shield" in self.player2_items:
            self.player2_max_health = 120
            self.player2_health = 120
            
    def attack_player1(self):
        """Appelé quand le joueur 1 appuie sur ESPACE ou X (manette)"""
        if not self.combat_active:
            return
        if not self.player1_attacking:
            self.player1_attacking = True
            self.attack_timer = 0
            self._player1_attack()
    
    def attack_player2(self):
        """Appelé quand le joueur 2 appuie sur ENTRÉE ou X (manette)"""
        if not self.combat_active:
            return
        if not self.player2_attacking:
            self.player2_attacking = True
            self.attack_timer = 0
            self._player2_attack()
    
    def update(self, keys, player2_keys=None, player1_attack=False, player2_attack=False):
        """Met à jour le combat. player1_attack/player2_attack = manette (bouton X) - DÉPRÉCIÉ, utiliser attack_player1/2"""
        if not self.combat_active:
            return
        
        self.combat_timer += 1/60  # Incrémenter le timer (60 FPS)
        
        # Gérer les attaques du joueur 1 (clavier Espace - pour compatibilité)
        if keys and keys[pygame.K_SPACE] and not self.player1_attacking:
            self.attack_player1()
        
        # Gérer les attaques du joueur 2 (clavier Entrée - pour compatibilité)
        if self.match_manager.game_mode in ["2v1", "pvp"]:
            if player2_keys and player2_keys[pygame.K_RETURN] and not self.player2_attacking:
                self.attack_player2()
        
        # Gérer l'IA du bot
        if self.match_manager.game_mode in ["1v1", "2v1"]:
            self._bot_ai()
        
        # Réinitialiser les attaques après un délai (0.5 secondes entre chaque attaque)
        if self.attack_timer > 0.5:  # 0.5 secondes
            self.player1_attacking = False
            self.player2_attacking = False
            self.bot_attacking = False
        else:
            self.attack_timer += 1/60
        
        # Vérifier les conditions de fin de combat
        winner = self._check_winner()
        if winner or self.combat_timer >= self.max_combat_time:
            self.combat_active = False
            if not winner:
                # Timeout - le joueur avec le plus de HP gagne
                if self.match_manager.game_mode == "pvp":
                    if self.player1_health > self.player2_health:
                        winner = "player1"
                    elif self.player2_health > self.player1_health:
                        winner = "player2"
                    else:
                        winner = "tie"
                else:
                    if self.player1_health > self.bot_health:
                        winner = "player1"
                    else:
                        winner = "bot"
            
            # Ne pas appeler complete_combat ici - c'est géré par _handle_minigame_winner dans game.py
            return winner
        
        return None
    
    def _player1_attack(self):
        """Le joueur 1 attaque"""
        damage = 20
        if "speed_boost" in self.player1_items:
            damage = 25  # Plus de dégâts avec speed boost
        
        if self.match_manager.game_mode == "pvp":
            self.player2_health -= damage
            if self.player2_health < 0:
                self.player2_health = 0
        else:
            self.bot_health -= damage
            if self.bot_health < 0:
                self.bot_health = 0
    
    def _player2_attack(self):
        """Le joueur 2 attaque"""
        damage = 20
        if "speed_boost" in self.player2_items:
            damage = 25
        
        if self.match_manager.game_mode == "pvp":
            self.player1_health -= damage
            if self.player1_health < 0:
                self.player1_health = 0
        else:
            self.bot_health -= damage
            if self.bot_health < 0:
                self.bot_health = 0
    
    def _bot_ai(self):
        """IA du bot pour le combat"""
        # Le bot attaque toutes les 2 secondes
        if random.random() < 0.02:  # ~2% de chance par frame (environ toutes les 2 secondes)
            self.bot_attacking = True
            self.attack_timer = 0
            
            damage = 15
            if self.match_manager.game_mode == "2v1":
                # En mode 2v1, le bot attaque les deux joueurs
                self.player1_health -= damage
                self.player2_health -= damage
            else:
                self.player1_health -= damage
            
            if self.player1_health < 0:
                self.player1_health = 0
            if self.player2_health < 0:
                self.player2_health = 0
    
    def _check_winner(self):
        """Vérifie s'il y a un gagnant"""
        if self.match_manager.game_mode == "pvp":
            if self.player1_health <= 0:
                return "player2"
            elif self.player2_health <= 0:
                return "player1"
        else:
            if self.player1_health <= 0:
                return "bot"
            elif self.bot_health <= 0:
                return "player1"
            elif self.match_manager.game_mode == "2v1" and self.player2_health <= 0:
                # En mode 2v1, si les deux joueurs sont KO, le bot gagne
                if self.player1_health <= 0:
                    return "bot"
        
        return None
    
    def draw(self, screen):
        """Dessine l'interface de combat"""
        if not self.combat_active:
            return
        
        # Fond sombre pour le combat
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Titre - Mini-jeu combat pour déterminer le gagnant
        font_large = pygame.font.Font(None, 52)
        title = font_large.render("🎮 MINI-JEU COMBAT 🎮", True, ORANGE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        subtitle = pygame.font.Font(None, 24).render("Qui gagne la manche?", True, YELLOW)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 75))
        
        # Timer
        font = pygame.font.Font(None, 36)
        time_left = int(self.max_combat_time - self.combat_timer)
        timer_text = font.render(f"Temps: {time_left}s", True, WHITE)
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 100))
        
        # Barres de vie
        bar_width = 300
        bar_height = 30
        bar_y = 200
        
        # Joueur 1
        self._draw_health_bar(screen, 100, bar_y, bar_width, bar_height,
                             self.player1_health, self.player1_max_health, "Joueur 1", BLUE)
        
        # Joueur 2 ou Bot
        if self.match_manager.game_mode == "pvp":
            self._draw_health_bar(screen, SCREEN_WIDTH - 400, bar_y, bar_width, bar_height,
                                 self.player2_health, self.player2_max_health, "Joueur 2", GREEN)
        else:
            self._draw_health_bar(screen, SCREEN_WIDTH - 400, bar_y, bar_width, bar_height,
                                 self.bot_health, self.bot_max_health, "Bot", RED)
        
        # Instructions claires - COMMENT JOUER
        font_small = pygame.font.Font(None, 26)
        font_tiny = pygame.font.Font(None, 22)
        
        how_to_title = font_small.render("COMMENT JOUER :", True, YELLOW)
        screen.blit(how_to_title, (SCREEN_WIDTH // 2 - how_to_title.get_width() // 2, 260))
        
        if self.match_manager.game_mode == "pvp":
            instructions = [
                "Joueur 1 : ESPACE ou X (manette) = ATTAQUER",
                "Joueur 2 : ENTRÉE ou X (manette) = ATTAQUER",
                "",
                "💡 APPUYEZ BRIÈVEMENT (tap) sur X ou ESPACE",
                "   Attendez 0.5 seconde puis réappuyez pour enchaîner!",
                "",
                "Le premier à 0 PV perd. Temps limité : 30 secondes."
            ]
        else:
            instructions = [
                "ESPACE ou X (manette) = ATTAQUER le Bot",
                "",
                "💡 APPUYEZ BRIÈVEMENT (tap) sur X ou ESPACE",
                "   Attendez 0.5 seconde puis réappuyez pour enchaîner!",
                "   Chaque attaque = 20 dégâts",
                "",
                "Le premier à 0 PV perd. Temps limité : 30 secondes."
            ]
        
        y_offset = 295
        for instruction in instructions:
            if instruction:  # Ignorer les lignes vides
                color = CYAN if "💡" in instruction else WHITE
                text = font_tiny.render(instruction, True, color)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 25
        
        # Indicateurs d'attaque
        if self.player1_attacking:
            pygame.draw.circle(screen, YELLOW, (150, bar_y + bar_height // 2), 20)
        if self.player2_attacking or self.bot_attacking:
            x_pos = SCREEN_WIDTH - 350 if self.match_manager.game_mode == "pvp" else SCREEN_WIDTH - 350
            pygame.draw.circle(screen, YELLOW, (x_pos, bar_y + bar_height // 2), 20)
    
    def _draw_health_bar(self, screen, x, y, width, height, current, maximum, label, color):
        """Dessine une barre de vie"""
        # Label
        font = pygame.font.Font(None, 24)
        label_text = font.render(label, True, WHITE)
        screen.blit(label_text, (x, y - 25))
        
        # Fond de la barre
        pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height))
        
        # Barre de vie actuelle
        health_percentage = current / maximum
        fill_width = int(width * health_percentage)
        health_color = GREEN if health_percentage > 0.5 else YELLOW if health_percentage > 0.25 else RED
        pygame.draw.rect(screen, health_color, (x, y, fill_width, height))
        
        # Bordure
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Texte HP
        hp_text = font.render(f"{int(current)}/{maximum}", True, WHITE)
        screen.blit(hp_text, (x + width // 2 - hp_text.get_width() // 2, y + height // 2 - hp_text.get_height() // 2))

