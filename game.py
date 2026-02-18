"""
Classe principale du jeu - Gestion des états
"""
import pygame
from config import *
from player import Player
from level import Level
from scoreboard import Scoreboard
from menu import Menu
from settings import Settings
from settings_menu import SettingsMenu
from background import Background
from match_manager import MatchManager
from combat_system import CombatSystem
from rewards_system import RewardsSystem
from items_system import ItemsSystem
from race_system import RaceSystem
from game_modes import GameModes
from bot_ai import BotAI
from splash_screen import SplashScreen

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cyber Jump")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # États du jeu
        self.state = "splash"  # splash, menu, playing, game_over, scoreboard, enter_name, settings, mode_selection, competitive
        self.current_level_id = 0  # Progression linéaire : 0=Parcours1, 1=Parcours2, 2=Boss
        self.level_completed = False
        self.transition_timer = 0
        
        # Système compétitif
        self.game_modes = GameModes()
        self.match_manager = None
        self.combat_system = None
        self.rewards_system = None
        self.items_system = ItemsSystem()
        self.race_system = RaceSystem()
        self.bot_ai = None
        self.mode_selection_index = 0
        self.rounds_selection_index = 0
        self.difficulty_selection_index = 1  # Medium par défaut
        
        # Initialisation des composants
        self.settings = Settings()
        self.menu = Menu(self.screen)
        self.settings_menu = SettingsMenu(self.screen, self.settings)
        self.scoreboard = Scoreboard()
        self.background = Background()
        self.splash_screen = SplashScreen(self.screen)
        self.level = None
        self.player = None
        self.score = 0
        self.pseudo = ""
        self.entering_name = False
        self.name_input = ""
        self.camera_x = 0  # Position de la caméra pour suivre le joueur
        
        # Initialisation des manettes
        pygame.joystick.init()
        self.joystick = None
        self.joystick_available = False
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_available = True
            print(f"Manette détectée: {self.joystick.get_name()}")
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def start_game(self, level_id=0):
        """Démarre une nouvelle partie avec un niveau spécifique"""
        self.state = "playing"
        self.current_level_id = level_id
        # Ne pas passer LEVEL_FILE si le fichier n'existe pas, utiliser directement level_id
        self.level = Level(level_file=None, level_id=level_id)
        self.player = Player(50, 100)
        self.score = 0
        self.entering_name = False
        self.name_input = ""
        self.level_completed = False
    
    def handle_menu_events(self, event):
        """Gère les événements du menu"""
        # Gestion clavier
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
            return
        
        action = self.menu.handle_event(event)
        if action == "Mode Compétitif":
            self.state = "mode_selection"
            self.mode_selection_index = 0
        elif action == "Jouer":
            # Commencer depuis le niveau 1 (progression linéaire)
            self.start_game(0)
        elif action == "Scores":
            self.state = "scoreboard"
        elif action == "Paramètres":
            self.state = "settings"
        elif action == "Quitter":
            self.running = False
        
        # Gestion manette PS4 (si activée)
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                if event.type == pygame.JOYBUTTONDOWN:
                    # Bouton X (0) ou Croix pour sélectionner
                    if event.button == 0:
                        action = self.menu.options[self.menu.selected_option]
                        if action == "Jouer":
                            # Commencer depuis le niveau 1 (progression linéaire)
                            self.start_game(0)
                        elif action == "Scores":
                            self.state = "scoreboard"
                        elif action == "Paramètres":
                            self.state = "settings"
                        elif action == "Quitter":
                            self.running = False
                
                elif event.type == pygame.JOYHATMOTION:
                    # Flèches directionnelles (D-Pad) - vérifier que le hat existe
                    if event.joy < pygame.joystick.get_count():
                        joystick = pygame.joystick.Joystick(event.joy)
                        if joystick.get_numhats() > 0:
                            hat = joystick.get_hat(0)
                            if hat[1] == 1:  # Haut
                                self.menu.selected_option = (self.menu.selected_option - 1) % len(self.menu.options)
                            elif hat[1] == -1:  # Bas
                                self.menu.selected_option = (self.menu.selected_option + 1) % len(self.menu.options)
            except (AttributeError, IndexError, KeyError, pygame.error):
                pass  # Ignorer les erreurs de manette
    
    def handle_settings_events(self, event):
        """Gère les événements du menu paramètres"""
        # Gestion clavier
        result = self.settings_menu.handle_event(event)
        if result == "retour":
            self.state = "menu"
        
        # Gestion manette PS4 (si activée)
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                result = self.settings_menu.handle_joystick_event(event)
                if result == "retour":
                    self.state = "menu"
            except (AttributeError, IndexError, KeyError):
                pass  # Ignorer les erreurs de manette
    
    def handle_playing_events(self, event):
        """Gère les événements pendant le jeu"""
        # Gestion clavier - Saut et menu uniquement (mouvement géré dans update_game)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"
        
        # Gestion manette PS4 (si activée) - Saut et menu uniquement
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                if event.type == pygame.JOYBUTTONDOWN:
                    # Bouton X (0) pour sauter
                    if event.button == 0:
                        self.player.jump()
                    # Bouton Options (9) pour menu
                    elif event.button == 9:
                        self.state = "menu"
            except (AttributeError, IndexError, KeyError):
                pass  # Ignorer les erreurs de manette
    
    def handle_name_input_events(self, event):
        """Gère les événements de saisie du pseudo"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.name_input.strip():
                    self.pseudo = self.name_input.strip()
                    self.scoreboard.add_score(self.pseudo, self.score)
                    self.state = "scoreboard"
                    self.name_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
            else:
                if len(self.name_input) < 15:
                    self.name_input += event.unicode
    
    def update_competitive(self):
        """Met à jour le mode compétitif"""
        if self.match_manager and self.match_manager.round_state == "race":
            # Mettre à jour la course
            keys = pygame.key.get_pressed()
            
            # Mouvement du joueur
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_right()
            
            # Gestion manette
            if self.joystick_available and self.settings.joystick_enabled and self.joystick:
                try:
                    axis_x = self.joystick.get_axis(0)
                    deadzone = 0.3
                    if axis_x < -deadzone:
                        self.player.move_left()
                    elif axis_x > deadzone:
                        self.player.move_right()
                except (AttributeError, IndexError, pygame.error):
                    pass
            
            # Mettre à jour le joueur et le niveau
            if self.player and self.level:
                self.player.update(self.level.platforms)
                self.level.update(self.player)
                
                # Vérifier les collisions
                for collectible in self.level.collectibles:
                    if collectible.check_collision(self.player):
                        pass  # Les collectibles ne donnent plus de score en mode compétitif
                
                for enemy in self.level.enemies:
                    collision, crushed = enemy.check_collision_with_player(self.player)
                    if collision and not crushed:
                        self.player.lives -= 1
                        if self.player.lives > 0:
                            self.player.reset_position()
                        else:
                            # Perte de vie = retour au début de la course
                            self.player.lives = 5
                            self.player.reset_position()
            
            # Mettre à jour le système de course
            if self.race_system:
                self.race_system.update()
            
            # Mettre à jour les items
            if self.items_system:
                self.items_system.update()
        
        elif self.match_manager and self.match_manager.round_state == "rewards":
            if self.rewards_system:
                self.rewards_system.update()
        
        elif self.match_manager and self.match_manager.round_state == "combat":
            if self.combat_system:
                keys = pygame.key.get_pressed()
                self.combat_system.update(keys)
            if self.items_system:
                self.items_system.update()
    
    def handle_scoreboard_events(self, event):
        """Gère les événements du scoreboard"""
        # Gestion clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.state = "menu"
        
        # Gestion manette PS4 (si activée)
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                if event.type == pygame.JOYBUTTONDOWN:
                    # Bouton X (0) ou Options (9) pour retourner au menu
                    if event.button == 0 or event.button == 9:
                        self.state = "menu"
            except (AttributeError, IndexError, KeyError):
                pass  # Ignorer les erreurs de manette
    
    def update_game(self):
        """Met à jour l'état du jeu"""
        if self.state != "playing":
            return
        
        # Gestion du mouvement continu avec le clavier
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        elif keys[pygame.K_RIGHT]:
            self.player.move_right()
        
        # Gestion du stick analogique de la manette PS4 (mouvement continu, si activée)
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                # Stick gauche (axe 0 = horizontal)
                axis_x = self.joystick.get_axis(0)
                deadzone = 0.3  # Zone morte pour éviter les mouvements involontaires
                
                if axis_x < -deadzone:
                    self.player.move_left()
                elif axis_x > deadzone:
                    self.player.move_right()
                
                # D-Pad pour mouvement alternatif (vérifier que le hat existe)
                num_hats = self.joystick.get_numhats()
                if num_hats > 0:
                    hat = self.joystick.get_hat(0)
                    if hat[0] == -1:  # Gauche
                        self.player.move_left()
                    elif hat[0] == 1:  # Droite
                        self.player.move_right()
            except (AttributeError, IndexError, pygame.error):
                pass  # Ignorer les erreurs de manette
        
        # Mettre à jour le joueur
        self.player.update(self.level.platforms)
        
        # Mettre à jour le niveau
        self.level.update(self.player)
        
        # Vérifier les collisions avec les collectibles
        for collectible in self.level.collectibles:
            if collectible.check_collision(self.player):
                self.score += SCORE_COLLECTIBLE
        
        # Vérifier les collisions avec les ennemis
        for enemy in self.level.enemies:
            collision, crushed = enemy.check_collision_with_player(self.player)
            if collision:
                if crushed:
                    # Ennemi écrasé
                    enemy.alive = False
                    self.score += SCORE_ENEMY
                else:
                    # Joueur touché
                    self.player.lives -= 1
                    if self.player.lives > 0:
                        self.player.reset_position()
                    else:
                        # Game Over
                        self.state = "enter_name"
        
        # Vérifier les collisions avec le boss
        if self.level.boss:
            collision, crushed = self.level.boss.check_collision_with_player(self.player)
            if collision:
                if crushed:
                    # Boss écrasé (prend des dégâts)
                    self.level.boss.take_damage()
                    self.score += SCORE_ENEMY * 2  # Plus de points pour le boss
                    # Rebondir le joueur après avoir écrasé le boss
                    self.player.velocity_y = PLAYER_JUMP_STRENGTH * 0.7
                else:
                    # Joueur touché par le boss
                    self.player.lives -= 1
                    if self.player.lives > 0:
                        self.player.reset_position()
                    else:
                        # Game Over
                        self.state = "enter_name"
        
        # Vérifier si le niveau est terminé
        if self.level.check_level_complete(self.player):
            if not self.level_completed:
                self.level_completed = True
                self.transition_timer = 0
            
            # Si ce n'est pas le dernier niveau (boss), passer au suivant après transition
            if self.current_level_id < 2:  # 0=Parcours1, 1=Parcours2, 2=Boss
                self.transition_timer += 1
                if self.transition_timer > 180:  # 3 secondes à 60 FPS
                    # Passer au niveau suivant
                    self.current_level_id += 1
                    print(f"Chargement du niveau {self.current_level_id}...")  # Debug
                    # Ne pas passer LEVEL_FILE si le fichier n'existe pas, utiliser directement level_id
                    self.level = Level(level_file=None, level_id=self.current_level_id)
                    self.player.reset_position()
                    self.level_completed = False
                    self.transition_timer = 0
                    self.camera_x = 0  # Réinitialiser la caméra
                    print(f"Niveau {self.current_level_id} chargé!")  # Debug
            else:
                # Dernier niveau terminé (boss vaincu) - Fin du jeu
                self.transition_timer += 1
                if self.transition_timer > 120:  # 2 secondes avant d'afficher l'écran de fin
                    self.state = "enter_name"
    
    def draw_game(self):
        """Dessine l'état actuel du jeu"""
        if self.state == "splash":
            self.splash_screen.update()
            self.splash_screen.draw()
            if self.splash_screen.is_finished():
                self.state = "menu"
        elif self.state == "menu":
            self.menu.draw()
        
        elif self.state == "settings":
            self.settings_menu.draw()
        
        elif self.state == "mode_selection":
            self.draw_mode_selection()
        
        elif self.state == "competitive":
            self.draw_competitive_mode()
        
        elif self.state == "playing":
            # Mettre à jour la caméra pour suivre le joueur
            if self.player and self.level:
                # Centrer la caméra sur le joueur
                self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
                # Limiter la caméra aux limites du niveau
                max_camera_x = max(0, (self.level.end_x + 100) - SCREEN_WIDTH)
                self.camera_x = max(0, min(self.camera_x, max_camera_x))
            
            # Mettre à jour le fond
            self.background.update()
            
            # Dessiner le fond (ciel et nuages)
            self.background.draw(self.screen)
            
            # Dessiner le niveau avec décalage de caméra
            if self.level:
                self.level.draw(self.screen, camera_x=self.camera_x)
            
            # Dessiner le joueur avec décalage de caméra
            if self.player:
                old_x = self.player.rect.x
                self.player.rect.x -= self.camera_x
                self.player.draw(self.screen)
                self.player.rect.x = old_x
            
            # Interface utilisateur
            self.draw_ui()
        
        elif self.state == "enter_name":
            self.draw_enter_name()
        
        elif self.state == "scoreboard":
            self.draw_scoreboard()
        
        elif self.state == "game_over":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Dessine l'interface utilisateur pendant le jeu"""
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Vies
        lives_text = self.font_medium.render(f"Vies: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (20, 60))
        
        # Collectibles restants
        collectibles_left = sum(1 for c in self.level.collectibles if not c.collected)
        collectibles_text = self.font_small.render(
            f"Micro-puces: {collectibles_left}", True, YELLOW
        )
        self.screen.blit(collectibles_text, (20, 100))
        
        # Afficher le type de niveau en haut à droite
        if self.level:
            level_names = ["Parcours 1", "1v1 Combat", "Parcours 2"]
            level_name = level_names[self.current_level_id] if self.current_level_id < len(level_names) else "Niveau"
            level_text = self.font_medium.render(f"Niveau: {level_name}", True, YELLOW)
            self.screen.blit(level_text, (SCREEN_WIDTH - 250, 20))
            
            # Indicateur spécial pour le mode boss
            if self.level.level_type == "boss" and self.level.boss:
                if self.level.boss.alive:
                    boss_text = self.font_small.render("⚠ BOSS EN COURSE!", True, RED)
                    self.screen.blit(boss_text, (SCREEN_WIDTH - 250, 60))
                    # Afficher la barre de vie du boss
                    health_text = self.font_small.render(
                        f"Vie Boss: {self.level.boss.health}/{self.level.boss.max_health}", True, RED
                    )
                    self.screen.blit(health_text, (SCREEN_WIDTH - 250, 85))
        
        # Instructions
        level_type_hint = ""
        if self.level and self.level.level_type == "boss":
            level_type_hint = " | BOSS FINAL: Écrasez-le 3 fois!"
        elif self.level_completed and self.current_level_id < 2:
            level_type_hint = " | Niveau suivant..."
        
        if self.joystick_available and self.settings.joystick_enabled:
            inst_text = self.font_small.render(
                f"Clavier: Flèches/Space/ESC | Manette: Stick/Bouton X/Options | Double saut activé!{level_type_hint}", True, GRAY
            )
        else:
            inst_text = self.font_small.render(
                f"Flèches: Déplacer | Espace: Sauter (Double saut!) | ESC: Menu{level_type_hint}", True, GRAY
            )
        self.screen.blit(inst_text, (20, SCREEN_HEIGHT - 30))
        
        # Message de transition entre niveaux - Afficher "TERMINÉ" quand on touche le drapeau
        if self.level_completed:
            if self.current_level_id < 2:
                # Transition vers le niveau suivant
                next_level_names = ["Parcours 2", "BOSS FINAL"]
                next_level_name = next_level_names[self.current_level_id]
                transition_text = self.font_large.render("✓ NIVEAU TERMINÉ!", True, GREEN)
                next_text = self.font_medium.render(f"Prochain niveau: {next_level_name}", True, YELLOW)
                countdown = max(0, 3 - (self.transition_timer // 60))
                countdown_text = self.font_small.render(f"Chargement dans {countdown}...", True, CYAN)
                
                # Fond semi-transparent
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(200)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                transition_rect = transition_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                self.screen.blit(transition_text, transition_rect)
                self.screen.blit(next_text, next_rect)
                self.screen.blit(countdown_text, countdown_rect)
            else:
                # Boss vaincu - Victoire !
                victory_text = self.font_large.render("VICTOIRE!", True, YELLOW)
                boss_defeated_text = self.font_medium.render("BOSS VAINCU!", True, GREEN)
                
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(200)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
                boss_rect = boss_defeated_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
                
                self.screen.blit(victory_text, victory_rect)
                self.screen.blit(boss_defeated_text, boss_rect)
    
    def draw_enter_name(self):
        """Dessine l'écran de saisie du pseudo"""
        self.screen.fill(BLACK)
        
        # Titre
        title = self.font_large.render("Partie terminée !", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Score final
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        inst_text = self.font_small.render("Entrez votre pseudo:", True, GRAY)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(inst_text, inst_rect)
        
        # Zone de saisie
        input_text = self.font_medium.render(self.name_input + "_", True, CYAN)
        input_rect = input_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
        pygame.draw.rect(self.screen, DARK_GRAY, 
                        (input_rect.left - 10, input_rect.top - 5, 
                         input_rect.width + 20, input_rect.height + 10))
        self.screen.blit(input_text, input_rect)
        
        # Instructions
        enter_text = self.font_small.render("Appuyez sur Entrée pour valider", True, GRAY)
        enter_rect = enter_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(enter_text, enter_rect)
    
    def draw_scoreboard(self):
        """Dessine l'écran du scoreboard"""
        self.screen.fill(BLACK)
        
        # Titre
        title = self.font_large.render("TOP 10 SCORES", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # En-têtes
        header_y = 120
        headers = ["Rang", "Pseudo", "Score", "Date"]
        header_x = [100, 300, 600, 800]
        
        for i, header in enumerate(headers):
            text = self.font_small.render(header, True, GRAY)
            self.screen.blit(text, (header_x[i], header_y))
        
        # Ligne de séparation
        pygame.draw.line(self.screen, GRAY, (50, header_y + 30), (SCREEN_WIDTH - 50, header_y + 30), 2)
        
        # Scores
        top_scores = self.scoreboard.get_top_10()
        if not top_scores:
            no_scores = self.font_medium.render("Aucun score enregistré", True, GRAY)
            no_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_scores, no_rect)
        else:
            y_offset = header_y + 50
            for i, entry in enumerate(top_scores):
                rank_color = CYAN if i == 0 else WHITE
                
                # Rang
                rank_text = self.font_small.render(f"{i+1}.", True, rank_color)
                self.screen.blit(rank_text, (header_x[0], y_offset + i * 40))
                
                # Pseudo
                pseudo_text = self.font_small.render(entry["pseudo"], True, WHITE)
                self.screen.blit(pseudo_text, (header_x[1], y_offset + i * 40))
                
                # Score
                score_text = self.font_small.render(str(entry["score"]), True, YELLOW)
                self.screen.blit(score_text, (header_x[2], y_offset + i * 40))
                
                # Date
                date_text = self.font_small.render(entry["date"], True, GRAY)
                self.screen.blit(date_text, (header_x[3], y_offset + i * 40))
        
        # Instructions
        inst_text = self.font_small.render("Appuyez sur Entrée ou ESC pour retourner au menu", True, GRAY)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def draw_game_over(self):
        """Dessine l'écran de game over"""
        self.screen.fill(BLACK)
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(game_over_text, text_rect)
    
    def handle_mode_selection_events(self, event):
        """Gère les événements de sélection de mode"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.mode_selection_index = (self.mode_selection_index - 1) % len(self.game_modes.available_modes)
            elif event.key == pygame.K_DOWN:
                self.mode_selection_index = (self.mode_selection_index + 1) % len(self.game_modes.available_modes)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Sélectionner le mode
                mode_key = list(self.game_modes.available_modes.keys())[self.mode_selection_index]
                mode_info = self.game_modes.available_modes[mode_key]
                # Utiliser le premier nombre de manches disponible par défaut
                rounds = mode_info["rounds_options"][0]
                if self.game_modes.select_mode(mode_key, rounds):
                    self.start_competitive_match()
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"
    
    def start_competitive_match(self):
        """Démarre un match compétitif"""
        mode_key = list(self.game_modes.available_modes.keys())[self.mode_selection_index]
        rounds = self.game_modes.available_modes[mode_key]["rounds_options"][0]
        difficulty = ["easy", "medium", "hard"][self.difficulty_selection_index]
        
        # Initialiser les systèmes
        self.match_manager = MatchManager(mode_key, rounds)
        self.combat_system = CombatSystem(self.match_manager)
        self.rewards_system = RewardsSystem(self.match_manager)
        self.bot_ai = BotAI(difficulty)
        
        # Démarrer le match
        self.match_manager.start_match()
        self.state = "competitive"
        
        # Démarrer la première course
        self.start_race()
    
    def start_race(self):
        """Démarre une course"""
        # Utiliser un niveau aléatoire pour chaque manche (0 ou 1, pas le boss)
        import random
        level_id = random.randint(0, 1)
        self.current_level_id = level_id
        self.level = Level(level_file=None, level_id=level_id)
        self.player = Player(50, 100)
        self.race_system.start_race()
        self.match_manager.round_state = "race"
    
    def handle_competitive_events(self, event):
        """Gère les événements en mode compétitif"""
        keys = pygame.key.get_pressed()
        
        if self.match_manager.round_state == "race":
            # Gérer les événements de course
            self.handle_playing_events(event)
            
            # Vérifier si la course est terminée
            if self.level and self.level.check_level_complete(self.player):
                if not self.race_system.race_finished:
                    self.race_system.finish_race("player1")
                    # Simuler le temps du bot
                    bot_time = self.bot_ai.simulate_race_time(self.race_system.player1_time)
                    self.race_system.bot_time = bot_time
                    self.match_manager.complete_race(self.race_system.player1_time)
                    self.rewards_system.show_rewards()
        
        elif self.match_manager.round_state == "rewards":
            # Passer au combat après avoir vu les récompenses
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                self.combat_system.start_combat(
                    self.match_manager.current_rewards["player1"]["items"],
                    self.match_manager.current_rewards["player2"]["items"] if self.match_manager.current_rewards["player2"] else None
                )
        
        elif self.match_manager.round_state == "combat":
            # Gérer le combat
            player2_keys = None  # Pour le mode 2 joueurs
            winner = self.combat_system.update(keys, player2_keys)
            if winner:
                # Le combat est terminé, passer à la manche suivante ou finir le match
                if self.match_manager.is_match_complete():
                    self.state = "match_complete"
                else:
                    # Nouvelle course
                    self.start_race()
        
        elif self.match_manager.round_state == "match_complete":
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                self.state = "menu"
    
    def draw_mode_selection(self):
        """Dessine l'écran de sélection de mode"""
        self.screen.fill(SKY_BLUE)
        self.game_modes.draw_mode_selection(self.screen, self.mode_selection_index)
    
    def draw_competitive_mode(self):
        """Dessine le mode compétitif"""
        if self.match_manager.round_state == "race":
            # Dessiner la course normale avec le HUD de course
            # Mettre à jour la caméra
            if self.player and self.level:
                self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
                max_camera_x = max(0, (self.level.end_x + 100) - SCREEN_WIDTH)
                self.camera_x = max(0, min(self.camera_x, max_camera_x))
            
            self.background.update()
            self.background.draw(self.screen)
            
            if self.level:
                self.level.draw(self.screen, camera_x=self.camera_x)
            
            if self.player:
                old_x = self.player.rect.x
                self.player.rect.x -= self.camera_x
                self.player.draw(self.screen)
                self.player.rect.x = old_x
            
            # HUD de course
            self.race_system.update()
            self.race_system.draw_race_hud(self.screen, self.match_manager)
            
        elif self.match_manager.round_state == "rewards":
            # Dessiner les récompenses
            self.rewards_system.update()
            self.rewards_system.draw(self.screen)
        
        elif self.match_manager.round_state == "combat":
            # Dessiner le combat
            self.combat_system.draw(self.screen)
        
        elif self.match_manager.round_state == "match_complete":
            # Dessiner l'écran de fin de match
            self.draw_match_complete()
    
    def draw_match_complete(self):
        """Dessine l'écran de fin de match"""
        self.screen.fill(BLACK)
        
        winner = self.match_manager.get_match_winner()
        font_large = pygame.font.Font(None, 56)
        font_medium = pygame.font.Font(None, 36)
        
        # Titre
        title = font_large.render("MATCH TERMINÉ!", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Gagnant
        winner_texts = {
            "player1": "Joueur 1 a gagné!",
            "player2": "Joueur 2 a gagné!",
            "bot": "Le Bot a gagné!",
            "players": "Les Joueurs ont gagné!",
            "tie": "Match nul!"
        }
        winner_text = font_medium.render(winner_texts.get(winner, "Match terminé"), True, GREEN)
        self.screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, 200))
        
        # Scores finaux
        y_offset = 300
        scores = [
            f"Joueur 1: {self.match_manager.player1_wins} victoires",
        ]
        if self.match_manager.game_mode == "pvp":
            scores.append(f"Joueur 2: {self.match_manager.player2_wins} victoires")
        else:
            scores.append(f"Bot: {self.match_manager.bot_wins} victoires")
        
        for score in scores:
            text = font_medium.render(score, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 50
        
        # Instructions
        inst = self.font_small.render("Appuyez sur Entrée ou ESC pour retourner au menu", True, GRAY)
        self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def run(self):
        """Boucle principale du jeu"""
        # Ignorer les événements initiaux de la manette pour éviter le démarrage automatique
        pygame.event.clear()
        
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    
                    # Gérer les événements selon l'état
                    if self.state == "splash":
                        if self.splash_screen.handle_event(event):
                            self.state = "menu"
                    elif self.state == "menu":
                        self.handle_menu_events(event)
                    elif self.state == "settings":
                        self.handle_settings_events(event)
                    elif self.state == "playing":
                        self.handle_playing_events(event)
                    elif self.state == "enter_name":
                        self.handle_name_input_events(event)
                    elif self.state == "scoreboard":
                        self.handle_scoreboard_events(event)
                    elif self.state == "mode_selection":
                        self.handle_mode_selection_events(event)
                    elif self.state == "competitive":
                        self.handle_competitive_events(event)
                
                if not self.running:
                    break
                
                # Mettre à jour le jeu
                if self.state == "competitive":
                    self.update_competitive()
                else:
                    self.update_game()
                
                # Dessiner
                self.draw_game()
                
                # Contrôler le FPS
                self.clock.tick(FPS)
        finally:
            pygame.quit()
            import sys
            sys.exit(0)

