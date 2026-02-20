"""
Classe principale du jeu - Gestion des états
"""
import os
import datetime
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
from player_selection import PlayerSelection, UNASSIGNED
from tic_tac_toe_system import TicTacToeSystem
from lava_survival_system import LavaSurvivalSystem
from sound_manager import SoundManager
from progress import (
    get_joueur_vs_bot_progress,
    save_joueur_vs_bot_progress,
    reset_joueur_vs_bot_progress,
)

class Game:
    def __init__(self):
        pygame.init()
        # Mode plein écran : fenêtre sans bordure (pas exclusif) pour permettre Print Screen et captures
        self.fullscreen = True
        info = pygame.display.Info()
        self._display = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        self.display_w, self.display_h = self._display.get_size()
        # Surface de rendu du jeu (1200x800), mise à l'échelle pour remplir tout l'écran
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        self.tic_tac_toe_system = None
        self.lava_survival_system = None
        self.items_system = ItemsSystem()
        self.race_system = RaceSystem()
        self.bot_ai = None
        self.sound_manager = SoundManager()  # Gestionnaire de sons
        self.sound_manager = SoundManager()  # Gestionnaire de sons
        self.mode_selection_index = 0
        self.rounds_selection_index = 0
        self.difficulty_selection_index = 1  # Medium par défaut
        
        # Sélection des joueurs (mode 2J) : qui contrôle J1/J2
        self.player_selection = None
        self.player1_joy_id = 0   # 0 ou 1 = manette, None = clavier
        self.player2_joy_id = 1   # Par défaut: manette 0 = J1, manette 1 = J2
        
        # Course et Combat - sous-menus
        self.course_combat_options = ["Course seule", "Combat seul"]
        self.course_combat_index = 0
        self.course_options = ["Parcours 1", "Parcours 2", "Boss"]
        self.course_choice_index = 0
        self.combat_options = ["vs Joueur", "vs Bot"]
        self.combat_choice_index = 0
        self.combat_only_mode = False  # True quand on fait un combat seul (Course et Combat)
        self.course_only_completed = False  # Course seule terminée
        
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
        
        # Initialisation des manettes (J1=manette 0, J2=manette 1 si disponible)
        pygame.joystick.init()
        self.joystick = None
        self.joystick2 = None
        self.joystick_available = False
        self.joystick2_available = False
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_available = True
            print(f"Manette 1: {self.joystick.get_name()}")
        if pygame.joystick.get_count() > 1:
            self.joystick2 = pygame.joystick.Joystick(1)
            self.joystick2.init()
            self.joystick2_available = True
            print(f"Manette 2: {self.joystick2.get_name()}")
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def toggle_fullscreen(self):
        """Basculer entre mode plein écran et fenêtré"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            info = pygame.display.Info()
            self._display = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
            self.display_w, self.display_h = self._display.get_size()
        else:
            self.display_w, self.display_h = SCREEN_WIDTH, SCREEN_HEIGHT
            self._display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def get_joy_for_player1(self):
        """Retourne le joystick du Joueur 1 (ou None si clavier). Utilise les manettes pré-initialisées."""
        if self.player1_joy_id is None or self.player1_joy_id == UNASSIGNED:
            return None
        if not self.settings.joystick_enabled:
            return None
        try:
            if self.player1_joy_id == 0 and self.joystick_available and self.joystick:
                return self.joystick
            elif self.player1_joy_id == 1 and self.joystick2_available and self.joystick2:
                return self.joystick2
            else:
                # Essayer de récupérer directement depuis pygame si les manettes pré-initialisées ne fonctionnent pas
                if pygame.joystick.get_count() > self.player1_joy_id:
                    joy = pygame.joystick.Joystick(self.player1_joy_id)
                    if joy.get_init():
                        return joy
        except (AttributeError, pygame.error, IndexError) as e:
            print(f"[DEBUG] Erreur get_joy_for_player1 (joy_id={self.player1_joy_id}): {e}")
        return None
    
    def get_joy_for_player2(self):
        """Retourne le joystick du Joueur 2 (ou None si clavier). Utilise les manettes pré-initialisées."""
        if self.player2_joy_id is None or self.player2_joy_id == UNASSIGNED:
            return None
        if not self.settings.joystick_enabled:
            return None
        try:
            if self.player2_joy_id == 0 and self.joystick_available and self.joystick:
                return self.joystick
            elif self.player2_joy_id == 1 and self.joystick2_available and self.joystick2:
                return self.joystick2
            else:
                # Essayer de récupérer directement depuis pygame si les manettes pré-initialisées ne fonctionnent pas
                if pygame.joystick.get_count() > self.player2_joy_id:
                    joy = pygame.joystick.Joystick(self.player2_joy_id)
                    if joy.get_init():
                        return joy
        except (AttributeError, pygame.error, IndexError) as e:
            print(f"[DEBUG] Erreur get_joy_for_player2 (joy_id={self.player2_joy_id}): {e}")
        return None
    
    def _get_axis_or_hat_x(self, joy):
        """Retourne la valeur X du mouvement (-1, 0, 1) : stick gauche ou D-Pad"""
        try:
            axis_x = joy.get_axis(0)
            if abs(axis_x) > 0.3:
                return -1 if axis_x < 0 else 1
        except (AttributeError, IndexError, pygame.error):
            pass
        try:
            if joy.get_numhats() > 0:
                hat = joy.get_hat(0)
                if hat[0] != 0:
                    return hat[0]
        except (AttributeError, IndexError, pygame.error):
            pass
        return 0
    
    def _take_screenshot(self):
        """Sauvegarde une capture d'écran dans le dossier du jeu"""
        folder = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(os.path.join(folder, "screenshots"), exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, "screenshots", f"cyberjump_{ts}.png")
        pygame.image.save(self._display, path)
        print(f"Capture sauvegardée: {path}")
    
    def start_game(self, level_id=0):
        """Démarre une nouvelle partie avec un niveau spécifique"""
        # Demander le pseudo AVANT de commencer si pas encore défini
        if not self.pseudo or not self.pseudo.strip():
            self.name_input = ""
            self.state = "enter_name_before_match"
            self._pending_start_game_level_id = level_id  # Sauvegarder le level_id pour après
            return
        
        # Pseudo déjà défini, démarrer directement
        self.state = "playing"
        self.current_level_id = level_id
        # Ne pas passer LEVEL_FILE si le fichier n'existe pas, utiliser directement level_id
        self.level = Level(level_file=None, level_id=level_id)
        self.player = Player(50, 100)
        self.score = 0
        self.entering_name = False
        self.name_input = ""
        self.level_completed = False
    
    def start_joueur_vs_bot(self, continue_progress=True):
        """Démarre Joueur vs Bot - continue ou nouvelle partie"""
        # Demander le pseudo AVANT de commencer si pas encore défini
        if not self.pseudo or not self.pseudo.strip():
            self.name_input = ""
            self.state = "enter_name_before_match"
            self._pending_start_joueur_vs_bot = continue_progress  # Sauvegarder pour après
            return
        
        # Pseudo déjà défini, continuer normalement
        if not continue_progress:
            reset_joueur_vs_bot_progress()
        
        progress = get_joueur_vs_bot_progress()
        
        # Mode Joueur vs Bot: 1v1, 5 manches
        mode_key = "1v1"
        num_rounds = 5
        difficulty = ["easy", "medium", "hard"][self.difficulty_selection_index]
        
        self.match_manager = MatchManager(mode_key, num_rounds)
        self.combat_system = CombatSystem(self.match_manager)
        self.tic_tac_toe_system = TicTacToeSystem(self.match_manager)
        self.lava_survival_system = LavaSurvivalSystem(self.match_manager)
        self.rewards_system = RewardsSystem(
            self.match_manager,
            on_transition_to_combat=lambda: self._transition_rewards_to_minigame()
        )
        self.bot_ai = BotAI(difficulty)
        # Réinitialiser le flag de sauvegarde du score
        self._score_saved = False
        
        if progress and progress.get("match_complete"):
            # Match déjà terminé - afficher l'écran de fin
            self.match_manager.load_state(
                progress["current_round"],
                progress["player1_wins"],
                progress["bot_wins"],
                match_complete=True
            )
            self.state = "competitive"
        elif progress and not progress.get("match_complete"):
            # Reprendre la progression
            self.match_manager.load_state(
                progress["current_round"],
                progress["player1_wins"],
                progress["bot_wins"],
                match_complete=False
            )
            self.state = "competitive"
            self.start_race()
        else:
            # Nouvelle partie - start_match met round_state = "round_intro" (Manche 1)
            self.match_manager.start_match()
            self.state = "competitive"
            if self.match_manager.round_state != "round_intro":
                self.start_race()
    
    def handle_menu_events(self, event):
        """Gère les événements du menu"""
        # Gestion clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return
            elif event.key == pygame.K_F11:
                # Basculer entre plein écran et fenêtré
                self.toggle_fullscreen()
        
        action = self.menu.handle_event(event)
        if action == "Mode Compétitif":
            self.state = "mode_selection"
            self.mode_selection_index = 0
        elif action == "Jouer":
            # Joueur vs Bot - continuer la progression sauvegardée
            self.start_joueur_vs_bot(continue_progress=True)
        elif action == "Nouvelle partie":
            # Joueur vs Bot - réinitialiser et recommencer
            self.start_joueur_vs_bot(continue_progress=False)
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
                            self.start_joueur_vs_bot(continue_progress=True)
                        elif action == "Nouvelle partie":
                            self.start_joueur_vs_bot(continue_progress=False)
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
                self.sound_manager.play_jump()  # Son de saut
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"
            elif event.key == pygame.K_F11:
                # Basculer entre plein écran et fenêtré
                self.toggle_fullscreen()
        
        # Gestion manette - Saut J1 (bouton X/Square) et menu (Options)
        if self.settings.joystick_enabled and event.type == pygame.JOYBUTTONDOWN:
            try:
                joy_id = getattr(event, 'joy', 0)
                j1_id = self.player1_joy_id if (self.state == "competitive" and self.player1_joy_id is not None) else 0
                if joy_id == j1_id:
                    if event.button in (0, 2):  # X ou Square = saut
                        self.player.jump()
                        self.sound_manager.play_jump()  # Son de saut
                    elif event.button == 9 and self.state != "competitive":
                        self.state = "menu"
            except (AttributeError, IndexError, KeyError):
                pass
    
    def handle_name_input_events(self, event):
        """Gère les événements de saisie du pseudo"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.name_input.strip():
                    self.pseudo = self.name_input.strip()
                    # Si on est dans l'état "enter_name_before_match", démarrer le jeu
                    if self.state == "enter_name_before_match":
                        self.name_input = ""
                        
                        # Vérifier quel mode démarrer
                        if hasattr(self, '_pending_start_game_level_id'):
                            # Mode classique (start_game)
                            level_id = self._pending_start_game_level_id
                            delattr(self, '_pending_start_game_level_id')
                            self.state = "playing"
                            self.current_level_id = level_id
                            self.level = Level(level_file=None, level_id=level_id)
                            self.player = Player(50, 100)
                            self.score = 0
                            self.entering_name = False
                            self.level_completed = False
                        elif hasattr(self, '_pending_start_joueur_vs_bot'):
                            # Mode Joueur vs Bot
                            continue_progress = self._pending_start_joueur_vs_bot
                            delattr(self, '_pending_start_joueur_vs_bot')
                            # Appeler start_joueur_vs_bot qui va maintenant démarrer directement
                            self.start_joueur_vs_bot(continue_progress)
                        elif hasattr(self, 'match_manager') and self.match_manager:
                            # Mode compétitif (déjà initialisé)
                            num_joy = pygame.joystick.get_count()
                            self.player1_joy_id = 0 if num_joy > 0 else None
                            self.player2_joy_id = None
                            self.state = "competitive"
                            if self.match_manager.round_state != "round_intro":
                                self.start_race()
                    else:
                        # État normal : après une partie, sauvegarder le score
                        if hasattr(self, 'match_manager') and self.match_manager:
                            boss_time = getattr(self, '_boss_victory_time', None)
                            self.scoreboard.add_score(self.pseudo, self.match_manager.player1_score, boss_time)
                        else:
                            # Mode classique
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
        # Sauvegarder automatiquement le score quand le match se termine (seulement une fois)
        if self.match_manager and self.match_manager.round_state == "match_complete":
            if not getattr(self, '_score_saved', False):
                # Sauvegarder le score même si le joueur a perdu (mode 1v1 seulement)
                if self.pseudo and self.match_manager.game_mode == "1v1":
                    winner = self.match_manager.get_match_winner()
                    # Si le joueur a gagné, sauvegarder avec le temps du boss
                    if not getattr(self.match_manager, 'match_lost', False) and winner == "player1":
                        boss_time = getattr(self, '_boss_victory_time', None)
                        self.scoreboard.add_score(self.pseudo, self.match_manager.player1_score, boss_time)
                        print(f"[DEBUG] Score sauvegardé automatiquement (victoire): {self.pseudo} - {self.match_manager.player1_score} pts - Temps boss: {boss_time}")
                    # Si le joueur a perdu, sauvegarder quand même le score avec le temps écoulé
                    elif getattr(self.match_manager, 'match_lost', False):
                        defeat_time = getattr(self, '_boss_defeat_time', None)
                        # Si pas de temps capturé, utiliser 195 secondes (timeout)
                        if defeat_time is None:
                            defeat_time = 195.0
                        self.scoreboard.add_score(self.pseudo, self.match_manager.player1_score, defeat_time)
                        print(f"[DEBUG] Score sauvegardé automatiquement (défaite): {self.pseudo} - {self.match_manager.player1_score} pts - Temps écoulé: {defeat_time:.2f}s")
                    self._score_saved = True
            return  # Ne pas continuer la mise à jour si le match est terminé
        
        if self.match_manager and self.match_manager.round_state == "race":
            # Attendre la fin de l'animation "Manche X" avant de jouer (MAX 3 secondes)
            if getattr(self, '_race_intro_timer', 0) > 0:
                self._race_intro_timer -= 1
                # Si c'est la manche 5 (boss) et que l'animation vient de se terminer, initialiser le timer
                if self.level and self.level.level_type == "boss" and self._race_intro_timer == 0:
                    if self.level.boss_start_time is None:
                        self.level.boss_start_time = pygame.time.get_ticks()
                        print(f"[DEBUG] Timer boss démarré (après animation Manche 5)")
                return  # Pas de jeu tant que l'animation n'est pas terminée
            
            keys = pygame.key.get_pressed()
            
            # Joueur 1: Clavier (Flèches/A/D) OU Manette 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_right()
            # Joueur 1: Clavier OU Manette (stick ou D-Pad)
            joy1 = self.get_joy_for_player1()
            if joy1:
                dx = self._get_axis_or_hat_x(joy1)
                if dx < 0:
                    self.player.move_left()
                elif dx > 0:
                    self.player.move_right()
            
            # Joueur 2: Clavier (J/L) OU Manette (stick ou D-Pad)
            if self.player2:
                if keys[pygame.K_j]:
                    self.player2.move_left()
                if keys[pygame.K_l]:
                    self.player2.move_right()
                joy2 = self.get_joy_for_player2()
                if joy2:
                    dx = self._get_axis_or_hat_x(joy2)
                    if dx < 0:
                        self.player2.move_left()
                    elif dx > 0:
                        self.player2.move_right()
            
            # Mise à jour physique et collisions
            if self.match_manager.game_mode == "pvp" and self.player2:
                # PvP: MÊME NIVEAU pour les deux (level2 = level)
                self.player.update(self.level.platforms)
                self.player2.update(self.level.platforms)
                self.level.update(self.player)  # Une seule mise à jour (ennemis partagés)
                self.level.check_checkpoint(self.player)
                self.level.check_checkpoint(self.player2)
                for c in self.level.collectibles:
                    if c.check_collision(self.player):
                        if getattr(c, 'collect_type', 'speed') == 'speed':
                            self.player.stars_collected += 1
                        elif getattr(c, 'collect_type', '') == 'kill_ground':
                            # Étoile rouge : bouclier pour tuer les ennemis au sol pendant 3 secondes
                            self.player.ground_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        elif getattr(c, 'collect_type', '') == 'kill_flying':
                            # Étoile bleue : bouclier pour tuer les ennemis volants pendant 3 secondes
                            self.player.flying_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        else:
                            self._apply_jump_bonus(self.player)
                        self.sound_manager.play_collectible()  # Son de collectible
                    elif c.check_collision(self.player2):
                        if getattr(c, 'collect_type', 'speed') == 'speed':
                            self.player2.stars_collected += 1
                        elif getattr(c, 'collect_type', '') == 'kill_ground':
                            # Étoile rouge : bouclier pour tuer les ennemis au sol pendant 3 secondes
                            self.player2.ground_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player2.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player2.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        elif getattr(c, 'collect_type', '') == 'kill_flying':
                            # Étoile bleue : bouclier pour tuer les ennemis volants pendant 3 secondes
                            self.player2.flying_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player2.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player2.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        else:
                            self._apply_jump_bonus(self.player2)
                        self.sound_manager.play_collectible()  # Son de collectible
                if self.level.level_type == "boss" and hasattr(self.level, 'bounds_x'):
                    for p in [self.player, self.player2]:
                        p.rect.x = max(self.level.bounds_x[0], min(p.rect.x, self.level.bounds_x[1] - p.rect.width))
                for e in self.level.enemies:
                    col1, crushed1 = e.check_collision_with_player(self.player)
                    col2, crushed2 = e.check_collision_with_player(self.player2)
                    # Manches 1-4 : ennemis invincibles (pas de kill, seulement dégâts)
                    # Manche 5 : ennemis tuables avec boucliers temporaires (3 secondes)
                    current_round = self.match_manager.current_round if self.match_manager else 1
                    is_ground_enemy = not getattr(e, 'flying', False)
                    is_flying_enemy = getattr(e, 'flying', False)
                    
                    # Vérifier les boucliers actifs pour le joueur 1
                    has_ground_shield = current_round == 5 and getattr(self.player, 'ground_shield_timer', 0) > 0
                    has_flying_shield = current_round == 5 and getattr(self.player, 'flying_shield_timer', 0) > 0
                    can_kill1 = (has_ground_shield and is_ground_enemy) or (has_flying_shield and is_flying_enemy)
                    
                    if col1:
                        if can_kill1:
                            # Avec bouclier actif : toucher l'ennemi = le tuer (pas besoin d'être au-dessus)
                            e.alive = False
                            self.sound_manager.play_enemy_kill()  # Son de mort d'ennemi
                        else:
                            # Ennemi invincible ou pas de bouclier actif : dégâts au joueur
                            self.player.lives -= 1
                            self.sound_manager.play_player_hit()  # Son quand le joueur est touché
                            if self.player.lives <= 0:
                                self.player.lives = 5
                            self.player.reset_to_checkpoint()
                    
                    # Vérifier les boucliers actifs pour le joueur 2
                    if col2:
                        has_ground_shield2 = current_round == 5 and getattr(self.player2, 'ground_shield_timer', 0) > 0
                        has_flying_shield2 = current_round == 5 and getattr(self.player2, 'flying_shield_timer', 0) > 0
                        can_kill2 = (has_ground_shield2 and is_ground_enemy) or (has_flying_shield2 and is_flying_enemy)
                        
                        if can_kill2:
                            # Avec bouclier actif : toucher l'ennemi = le tuer (pas besoin d'être au-dessus)
                            e.alive = False
                            self.sound_manager.play_enemy_kill()  # Son de mort d'ennemi
                        else:
                            # Ennemi invincible ou pas de bouclier actif : dégâts au joueur
                            self.player2.lives -= 1
                            self.sound_manager.play_player_hit()  # Son quand le joueur est touché
                            if self.player2.lives <= 0:
                                self.player2.lives = 5
                            self.player2.reset_to_checkpoint()
            elif self.player and self.level:
                self.player.update(self.level.platforms)
                if self.player2:
                    self.player2.update(self.level.platforms)
                self.level.update(self.player)
                self.level.check_checkpoint(self.player)
                if self.player2:
                    self.level.check_checkpoint(self.player2)
                for c in self.level.collectibles:
                    if c.check_collision(self.player):
                        if getattr(c, 'collect_type', 'speed') == 'speed':
                            self.player.stars_collected += 1
                        elif getattr(c, 'collect_type', '') == 'kill_ground':
                            # Étoile rouge : bouclier pour tuer les ennemis au sol pendant 3 secondes
                            self.player.ground_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        elif getattr(c, 'collect_type', '') == 'kill_flying':
                            # Étoile bleue : bouclier pour tuer les ennemis volants pendant 3 secondes
                            self.player.flying_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        else:
                            self._apply_jump_bonus(self.player)
                    elif self.player2 and c.check_collision(self.player2):
                        if getattr(c, 'collect_type', 'speed') == 'speed':
                            self.player2.stars_collected += 1
                        elif getattr(c, 'collect_type', '') == 'kill_ground':
                            # Étoile rouge : bouclier pour tuer les ennemis au sol pendant 3 secondes
                            self.player2.ground_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player2.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player2.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        elif getattr(c, 'collect_type', '') == 'kill_flying':
                            # Étoile bleue : bouclier pour tuer les ennemis volants pendant 3 secondes
                            self.player2.flying_shield_timer = 180  # 3 secondes = 180 frames à 60 FPS
                            self.player2.bubbles_timer = 180  # Effet de bulles pendant 3 secondes
                            self.player2.bubbles = []  # Réinitialiser les bulles
                            self.sound_manager.play_collectible()  # Son de collectible
                        else:
                            self._apply_jump_bonus(self.player2)
                if self.level.level_type == "boss" and hasattr(self.level, 'bounds_x'):
                    for p in [self.player] + ([self.player2] if self.player2 else []):
                        p.rect.x = max(self.level.bounds_x[0], min(p.rect.x, self.level.bounds_x[1] - p.rect.width))
                for e in self.level.enemies:
                    col, crushed = e.check_collision_with_player(self.player)
                    # Manches 1-4 : ennemis invincibles (pas de kill, seulement dégâts)
                    # Manche 5 : ennemis tuables avec boucliers temporaires (3 secondes)
                    current_round = self.match_manager.current_round if self.match_manager else 1
                    is_ground_enemy = not getattr(e, 'flying', False)
                    is_flying_enemy = getattr(e, 'flying', False)
                    
                    # Vérifier les boucliers actifs pour le joueur 1
                    has_ground_shield = current_round == 5 and getattr(self.player, 'ground_shield_timer', 0) > 0
                    has_flying_shield = current_round == 5 and getattr(self.player, 'flying_shield_timer', 0) > 0
                    can_kill = (has_ground_shield and is_ground_enemy) or (has_flying_shield and is_flying_enemy)
                    
                    if col:
                        if can_kill:
                            # Avec bouclier actif : toucher l'ennemi = le tuer (pas besoin d'être au-dessus)
                            e.alive = False
                            self.sound_manager.play_enemy_kill()  # Son de mort d'ennemi
                        else:
                            # Ennemi invincible ou pas de bouclier actif : dégâts au joueur
                            self.player.lives -= 1
                            self.sound_manager.play_player_hit()  # Son quand le joueur est touché
                            if self.player.lives <= 0:
                                self.player.lives = 5
                            self.player.reset_to_checkpoint()
                    if self.player2:
                        col2, crushed2 = e.check_collision_with_player(self.player2)
                        has_ground_shield2 = current_round == 5 and getattr(self.player2, 'ground_shield_timer', 0) > 0
                        has_flying_shield2 = current_round == 5 and getattr(self.player2, 'flying_shield_timer', 0) > 0
                        can_kill2 = (has_ground_shield2 and is_ground_enemy) or (has_flying_shield2 and is_flying_enemy)
                        if col2:
                            if can_kill2:
                                # Avec bouclier actif : toucher l'ennemi = le tuer (pas besoin d'être au-dessus)
                                e.alive = False
                                self.sound_manager.play_enemy_kill()  # Son de mort d'ennemi
                            else:
                                # Ennemi invincible ou pas de bouclier actif : dégâts au joueur
                                self.player2.lives -= 1
                                self.sound_manager.play_player_hit()  # Son quand le joueur est touché
                                if self.player2.lives <= 0:
                                    self.player2.lives = 5
                                self.player2.reset_to_checkpoint()
            
            if self.race_system:
                self.race_system.update()
            
            # Vérifier timeout boss (3min15) - défaite
            # IMPORTANT: Ne vérifier le timeout que si le niveau est vraiment démarré (pas pendant l'animation)
            if self.level and self.level.level_type == "boss" and getattr(self, '_race_intro_timer', 0) <= 0:
                if self.level.check_boss_timeout():
                    # Temps écoulé = défaite - capturer le temps écoulé
                    if hasattr(self.level, 'boss_start_time') and self.level.boss_start_time is not None:
                        elapsed_ms = pygame.time.get_ticks() - self.level.boss_start_time
                        elapsed_seconds = elapsed_ms / 1000.0
                        # Sauvegarder le temps écoulé (195 secondes = timeout)
                        self._boss_defeat_time = 195.0  # Temps maximum écoulé
                        print(f"[DEBUG] Timeout boss détecté, fin de partie - Temps écoulé: {elapsed_seconds:.2f}s")
                    else:
                        self._boss_defeat_time = 195.0  # Temps maximum par défaut
                    self.match_manager.round_state = "match_complete"
                    self.match_manager.match_lost = True  # Marquer comme perdu
                    return
            
            if self.items_system:
                self.items_system.update()
        
        elif self.match_manager and self.match_manager.round_state == "rewards":
            if self.rewards_system:
                self.rewards_system.update()
                # Après update(), vérifier si on est passé à round_intro (manche 4 → 5)
                # IMPORTANT: Si on vient de passer à round_intro, on doit gérer immédiatement
                # pour éviter que le jeu reste bloqué sur l'écran de récompenses
                if self.match_manager.round_state == "round_intro":
                    # Réinitialiser le timer et le flag pour la manche 5
                    # FORCER la réinitialisation pour éviter que le timer soit déjà à 150
                    self._round_intro_last_rnd = -1
                    self._round_intro_timer = 0
                    # Le bloc round_intro ci-dessous va gérer la suite
                    # Ne pas continuer ici, laisser le bloc round_intro gérer
        
        # Gérer round_intro (y compris la transition depuis rewards)
        # Utiliser if au lieu de elif pour gérer la transition dans le même frame
        if self.match_manager and self.match_manager.round_state == "round_intro":
            # Réinitialiser le timer quand on entre dans une nouvelle manche
            rnd = self.match_manager.current_round
            current_last_rnd = getattr(self, '_round_intro_last_rnd', -1)
            if current_last_rnd != rnd:
                # NOUVELLE MANCHE : réinitialiser complètement le timer
                print(f"[DEBUG] Nouvelle manche détectée: {rnd}, réinitialisation du timer")
                self._round_intro_last_rnd = rnd
                self._round_intro_timer = 0
                # IMPORTANT: Ne pas incrémenter le timer dans le même frame où on le réinitialise
                # pour éviter que start_race() soit appelé immédiatement
                # Ne pas faire return ici, laisser le code continuer pour les autres états
            else:
                # Même manche : incrémenter le timer seulement si on n'est pas dans une nouvelle manche
                current_timer = getattr(self, '_round_intro_timer', 0)
                # MAX 3 secondes (180 frames à 60 FPS) - ne JAMAIS dépasser
                if current_timer < 180:
                    self._round_intro_timer = current_timer + 1
                    if self._round_intro_timer % 30 == 0:  # Log toutes les 0.5 sec
                        print(f"[DEBUG] Timer round_intro: {self._round_intro_timer}/180")
                else:
                    # S'assurer que le timer ne dépasse JAMAIS 180 (MAX 3 secondes)
                    self._round_intro_timer = 180
                
                # Vérifier si le timer est écoulé (MAX 3 secondes) - transition automatique
                if self._round_intro_timer >= 180:
                    print(f"[DEBUG] Timer écoulé (MAX 3s atteint), démarrage de la course pour manche {rnd}")
                    # Réinitialiser les états
                    self.match_manager.race_completed = False
                    self.match_manager.rewards_shown = False
                    self.match_manager.combat_completed = False
                    self.match_manager.current_rewards = {
                        "player1": {"coins": 0, "items": []},
                        "player2": {"coins": 0, "items": []} if self.match_manager.game_mode in ["2v1", "pvp"] else None
                    }
                    # Démarrer la course (start_race() met round_state = "race")
                    try:
                        print(f"[DEBUG] Appel de start_race() pour manche {rnd}")
                        self.start_race()
                        print(f"[DEBUG] start_race() terminé, round_state={self.match_manager.round_state}")
                    except Exception as e:
                        print(f"[ERROR] Erreur lors du démarrage de la course: {e}")
                        import traceback
                        traceback.print_exc()
                    # Réinitialiser le timer
                    self._round_intro_timer = 0
                    self._round_intro_last_rnd = -1  # Réinitialiser pour la prochaine fois
        
        elif self.match_manager and self.match_manager.round_state == "combat":
            if self.combat_system:
                # S'assurer que le combat est démarré si nécessaire
                if not self.combat_system.combat_active:
                    self.combat_system.start_combat(
                        self.match_manager.current_rewards["player1"]["items"],
                        self.match_manager.current_rewards["player2"]["items"] if self.match_manager.current_rewards.get("player2") else None
                    )
                else:
                    keys = pygame.key.get_pressed()
                    player2_keys = keys if self.match_manager.game_mode in ["pvp", "2v1"] else None
                    # Les attaques sont gérées par événements (KEYDOWN/JOYBUTTONDOWN), pas ici
                    # On met juste à jour le combat
                    winner = self.combat_system.update(keys, player2_keys, player1_attack=False, player2_attack=False)
                    if winner:
                        # Le combat est terminé, gérer le gagnant
                        # Convertir "tie" en None pour la gestion des égalités
                        if winner == "tie":
                            winner = None
                        self._handle_minigame_winner(winner)
        
        elif self.match_manager and self.match_manager.round_state == "minigame_morpion":
            if self.tic_tac_toe_system:
                # IA du bot si nécessaire
                if self.match_manager.game_mode != "pvp" and self.tic_tac_toe_system.current_player == 'O' and not self.tic_tac_toe_system.game_over:
                    self.tic_tac_toe_system.bot_move()
                
                # Vérifier le gagnant
                if self.tic_tac_toe_system.game_over:
                    winner = self.tic_tac_toe_system.get_winner_for_match()
                    if winner:
                        self._handle_minigame_winner(winner)
        
        elif self.match_manager and self.match_manager.round_state == "minigame_lava":
            if self.lava_survival_system:
                keys = pygame.key.get_pressed()
                # Contrôles joueur 1
                p1_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
                p1_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
                # Contrôles joueur 2 (PvP)
                p2_left = keys[pygame.K_j] if self.match_manager.game_mode == "pvp" else False
                p2_right = keys[pygame.K_l] if self.match_manager.game_mode == "pvp" else False
                
                # Contrôles manette pour mouvement gauche/droite
                try:
                    joy1 = self.get_joy_for_player1()
                    if joy1:
                        axis_x = joy1.get_axis(0)  # Stick gauche horizontal
                        if axis_x < -0.3:
                            p1_left = True
                        elif axis_x > 0.3:
                            p1_right = True
                except (AttributeError, pygame.error):
                    pass
                
                if self.match_manager.game_mode == "pvp":
                    try:
                        joy2 = self.get_joy_for_player2()
                        if joy2:
                            axis_x = joy2.get_axis(0)
                            if axis_x < -0.3:
                                p2_left = True
                            elif axis_x > 0.3:
                                p2_right = True
                    except (AttributeError, pygame.error):
                        pass
                
                # Saut géré par événements (pas continu)
                self.lava_survival_system.update(
                    p1_left, p1_right, False,  # Jump géré par événements
                    p2_left, p2_right, False
                )
                
                # Vérifier le gagnant (une seule fois)
                if self.lava_survival_system.game_over and not getattr(self, '_lava_winner_handled', False):
                    winner = self.lava_survival_system.get_winner_for_match()
                    self._lava_winner_handled = True  # Marquer comme géré pour éviter les appels multiples
                    self._handle_minigame_winner(winner)  # Gère aussi None
            
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
        self.level.check_checkpoint(self.player)
        
        # Vérifier les collisions avec les collectibles
        for collectible in self.level.collectibles:
            if collectible.check_collision(self.player):
                if getattr(collectible, 'collect_type', 'speed') == 'speed':
                    self.player.stars_collected += 1
                else:
                    self._apply_jump_bonus(self.player)
        if self.level.level_type == "boss" and hasattr(self.level, 'bounds_x'):
            self.player.rect.x = max(self.level.bounds_x[0], min(self.player.rect.x, self.level.bounds_x[1] - self.player.rect.width))
        
        # Vérifier les collisions avec les ennemis
        for enemy in self.level.enemies:
            collision, crushed = enemy.check_collision_with_player(self.player)
            if collision:
                if crushed:
                    # Ennemi écrasé
                    enemy.alive = False
                    self.score += SCORE_ENEMY
                    self.sound_manager.play_enemy_kill()  # Son de mort d'ennemi
                else:
                    # Joueur touché - respawn au checkpoint
                    self.player.lives -= 1
                    self.sound_manager.play_player_hit()  # Son quand le joueur est touché
                    if self.player.lives > 0:
                        self.player.reset_to_checkpoint()
                    else:
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
                    # Joueur touché par le boss - respawn au checkpoint
                    self.player.lives -= 1
                    if self.player.lives > 0:
                        self.player.reset_to_checkpoint()
                    else:
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
        
        elif self.state == "course_combat_choice":
            self.draw_course_combat_choice()
        
        elif self.state == "course_choice":
            self.draw_course_choice()
        
        elif self.state == "combat_choice":
            self.draw_combat_choice()
        
        elif self.state == "course_only":
            self.draw_course_only()
        
        elif self.state == "combat_only":
            self.draw_combat_only()
        
        elif self.state == "player_selection":
            self.draw_player_selection()
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
        
        elif self.state == "enter_name" or self.state == "enter_name_before_match":
            self.draw_enter_name()
        
        elif self.state == "scoreboard":
            self.draw_scoreboard()
        
        elif self.state == "game_over":
            self.draw_game_over()
        
        # Mise à l'échelle pour remplir tout l'écran
        scaled = pygame.transform.smoothscale(self.screen, (self.display_w, self.display_h))
        self._display.blit(scaled, (0, 0))
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
        
        # Indicateur du bonus de saut (étoiles bleues)
        if self.player and getattr(self.player, 'jump_bonus_timer', 0) > 0:
            bonus_seconds = int(self.player.jump_bonus_timer / 60) + 1
            bonus_text = self.font_small.render(
                f"⭐ Bonus Saut Actif: {bonus_seconds}s - Tuez les ennemis en l'air!",
                True, CYAN
            )
            self.screen.blit(bonus_text, (20, 130))
        
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
        if self.state == "enter_name_before_match":
            input_y = 400
            enter_y = 500
        else:
            input_y = 450
            enter_y = 550
            
        input_text = self.font_medium.render(self.name_input + "_", True, CYAN)
        input_rect = input_text.get_rect(center=(SCREEN_WIDTH // 2, input_y))
        pygame.draw.rect(self.screen, DARK_GRAY, 
                        (input_rect.left - 10, input_rect.top - 5, 
                         input_rect.width + 20, input_rect.height + 10))
        self.screen.blit(input_text, input_rect)
        
        # Instructions
        enter_text = self.font_small.render("Appuyez sur Entrée pour valider", True, GRAY)
        enter_rect = enter_text.get_rect(center=(SCREEN_WIDTH // 2, enter_y))
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
        headers = ["Rang", "Pseudo", "Score", "Temps Boss", "Date"]
        header_x = [60, 220, 420, 620, 900]
        
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
            # Vérifier si le joueur actuel est dans le top 10
            current_player_in_top = False
            if self.pseudo:
                for entry in top_scores:
                    if entry["pseudo"].strip().lower() == self.pseudo.strip().lower():
                        current_player_in_top = True
                        break
            
            for i, entry in enumerate(top_scores):
                rank = i + 1
                rank_color = YELLOW if rank == 1 else (CYAN if rank <= 3 else WHITE)
                
                # Si c'est le joueur actuel, mettre en évidence
                is_current_player = self.pseudo and entry["pseudo"].strip().lower() == self.pseudo.strip().lower()
                if is_current_player:
                    rank_color = GREEN
                    # Fond coloré pour le joueur actuel
                    highlight_rect = pygame.Rect(header_x[0] - 10, y_offset - 5, SCREEN_WIDTH - header_x[0] - header_x[0] + 20, 35)
                    pygame.draw.rect(self.screen, (0, 50, 0), highlight_rect)
                    pygame.draw.rect(self.screen, GREEN, highlight_rect, 2)
                
                # Rang avec emoji pour le top 3
                rank_emoji = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else ""))
                rank_text = f"{rank_emoji} {rank}" if rank_emoji else str(rank)
                rank_surface = self.font_small.render(rank_text, True, rank_color)
                self.screen.blit(rank_surface, (header_x[0], y_offset))
                
                # Pseudo
                pseudo_text = self.font_small.render(entry["pseudo"], True, rank_color)
                self.screen.blit(pseudo_text, (header_x[1], y_offset))
                
                # Score
                score_text = self.font_small.render(str(entry["score"]), True, rank_color)
                self.screen.blit(score_text, (header_x[2], y_offset))
                
                # Temps du boss
                boss_time = entry.get("boss_time")
                if boss_time is not None:
                    time_minutes = int(boss_time // 60)
                    time_seconds = int(boss_time % 60)
                    time_milliseconds = int((boss_time % 1) * 1000)
                    time_str = f"{time_minutes:02d}:{time_seconds:02d}.{time_milliseconds:03d}"
                else:
                    time_str = "N/A"
                time_surface = self.font_small.render(time_str, True, rank_color)
                self.screen.blit(time_surface, (header_x[3], y_offset))
                
                # Date
                date_text = self.font_small.render(entry["date"], True, GRAY)
                self.screen.blit(date_text, (header_x[4], y_offset))
                
                y_offset += 40
            
            # Afficher le rang du joueur actuel s'il n'est pas dans le top 10
            if self.pseudo and not current_player_in_top:
                player_score = 0
                player_boss_time = None
                # Chercher le score du joueur actuel dans tous les scores (pas seulement top 10)
                all_scores = self.scoreboard.scores  # Tous les scores triés
                for entry in all_scores:
                    if entry["pseudo"].strip().lower() == self.pseudo.strip().lower():
                        player_score = entry["score"]
                        player_boss_time = entry.get("boss_time")
                        break
                
                if player_score > 0 or player_boss_time is not None:
                    player_rank = self.scoreboard.get_rank(player_score, player_boss_time)
                    if player_rank:
                        y_offset += 20
                        separator = self.font_small.render("─" * 50, True, GRAY)
                        self.screen.blit(separator, (SCREEN_WIDTH // 2 - separator.get_width() // 2, y_offset))
                        y_offset += 30
                        
                        rank_text = self.font_small.render(f"Votre classement: #{player_rank}", True, GREEN)
                        self.screen.blit(rank_text, (header_x[0], y_offset))
                        
                        pseudo_text = self.font_small.render(self.pseudo, True, GREEN)
                        self.screen.blit(pseudo_text, (header_x[1], y_offset))
                        
                        score_text = self.font_small.render(str(player_score), True, GREEN)
                        self.screen.blit(score_text, (header_x[2], y_offset))
                        
                        if player_boss_time is not None:
                            time_minutes = int(player_boss_time // 60)
                            time_seconds = int(player_boss_time % 60)
                            time_milliseconds = int((player_boss_time % 1) * 1000)
                            time_str = f"{time_minutes:02d}:{time_seconds:02d}.{time_milliseconds:03d}"
                        else:
                            time_str = "N/A"
                        time_surface = self.font_small.render(time_str, True, GREEN)
                        self.screen.blit(time_surface, (header_x[3], y_offset))
        
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
                mode_key = list(self.game_modes.available_modes.keys())[self.mode_selection_index]
                if mode_key == "course_combat":
                    # Sous-menu Course et Combat
                    self.state = "course_combat_choice"
                    self.course_combat_index = 0
                else:
                    # Joueur vs Joueur ou 2 Joueurs vs Bot
                    mode_info = self.game_modes.available_modes[mode_key]
                    rounds = mode_info["rounds_options"][0]
                    if self.game_modes.select_mode(mode_key, rounds):
                        self.start_competitive_match(mode_key)
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"
    
    def handle_player_selection_events(self, event):
        """Gère les événements de sélection des joueurs"""
        if not self.player_selection:
            return
        result = self.player_selection.handle_event(event)
        if result == "back":
            self.state = "menu"
            self.player_selection = None
        elif result == "ready":
            p1, p2 = self.player_selection.player1_joy_id, self.player_selection.player2_joy_id
            # Si conflit (même manette) : défaut J1=Manette1, J2=Manette2
            if p1 is not None and p2 is not None and p1 == p2:
                p1, p2 = 0, 1 if pygame.joystick.get_count() >= 2 else None
            self.player1_joy_id = p1
            self.player2_joy_id = p2
            print(f"[DEBUG] Assignation manettes: J1={p1}, J2={p2}, Total manettes={pygame.joystick.get_count()}")
            print(f"[DEBUG] Manette 0 disponible: {self.joystick_available}, Manette 1 disponible: {self.joystick2_available}")
            self.player_selection = None
            self.state = "competitive"
            # Ne pas appeler start_race() si round_intro (Manche 1) - l'intro s'affiche d'abord
            if self.match_manager.round_state != "round_intro":
                self.start_race()
    
    def update_player_selection(self):
        """Mise à jour de la sélection (délai auto si prêt)"""
        if self.player_selection and self.player_selection.is_ready():
            self._player_selection_timer = getattr(self, '_player_selection_timer', 0) + 1
            if self._player_selection_timer >= 90:  # ~1.5 sec
                p1, p2 = self.player_selection.player1_joy_id, self.player_selection.player2_joy_id
                if p1 is not None and p2 is not None and p1 == p2:
                    p1, p2 = 0, 1 if pygame.joystick.get_count() >= 2 else None
                self.player1_joy_id = p1
                self.player2_joy_id = p2
                print(f"[DEBUG] Assignation manettes (auto): J1={p1}, J2={p2}, Total manettes={pygame.joystick.get_count()}")
                print(f"[DEBUG] Manette 0 disponible: {self.joystick_available}, Manette 1 disponible: {self.joystick2_available}")
                self.player_selection = None
                self.state = "competitive"
                if self.match_manager.round_state != "round_intro":
                    self.start_race()
        else:
            self._player_selection_timer = 0
    
    def draw_player_selection(self):
        """Dessine l'écran de sélection des joueurs"""
        if self.player_selection:
            self.player_selection.draw()
    
    def start_competitive_match(self, mode_key=None):
        """Démarre un match compétitif (Joueur vs Joueur ou 2 Joueurs vs Bot)"""
        if mode_key is None:
            mode_key = list(self.game_modes.available_modes.keys())[self.mode_selection_index]
        if mode_key == "course_combat":
            return
        rounds = self.game_modes.available_modes[mode_key]["rounds_options"][0]
        difficulty = ["easy", "medium", "hard"][self.difficulty_selection_index]
        
        self.match_manager = MatchManager(mode_key, rounds)
        self.combat_system = CombatSystem(self.match_manager)
        self.tic_tac_toe_system = TicTacToeSystem(self.match_manager)
        self.lava_survival_system = LavaSurvivalSystem(self.match_manager)
        self.rewards_system = RewardsSystem(
            self.match_manager,
            on_transition_to_combat=lambda: self._transition_rewards_to_minigame()
        )
        self.bot_ai = BotAI(difficulty)
        
        self.match_manager.start_match()
        # Réinitialiser le flag de sauvegarde du score
        self._score_saved = False
        
        # Demander le pseudo AVANT de commencer (seulement pour le mode 1v1)
        if mode_key == "1v1":
            # Si le pseudo n'est pas encore défini, demander
            if not self.pseudo or not self.pseudo.strip():
                self.name_input = ""
                self.state = "enter_name_before_match"  # Nouvel état pour demander le pseudo avant le match
            else:
                # Pseudo déjà défini, continuer normalement
                num_joy = pygame.joystick.get_count()
                self.player1_joy_id = 0 if num_joy > 0 else None
                self.player2_joy_id = None
                self.state = "competitive"
                if self.match_manager.round_state != "round_intro":
                    self.start_race()
        else:
            # Mode 2 joueurs (pvp ou 2v1) : TOUJOURS écran de sélection
            num_joy = pygame.joystick.get_count()
            if mode_key in ["pvp", "2v1"]:
                # Chaque joueur choisit : manette (X/Cercle) ou clavier (Espace/Entrée)
                self.player_selection = PlayerSelection(self.screen, num_joy)
                self.state = "player_selection"
            else:
                # 1v1
                self.player1_joy_id = 0 if num_joy > 0 else None
                self.player2_joy_id = None
                self.state = "competitive"
                # Ne pas appeler start_race() si round_intro (Manche 1) - l'intro s'affiche d'abord
                if self.match_manager.round_state != "round_intro":
                    self.start_race()
    
    def _apply_jump_bonus(self, player):
        """Chaque étoile bleue : +1 saut (max 4) ET 5 secondes pour écraser les ennemis en l'air"""
        # Bonus de saut : +1 max_jumps (3 ou 4 au total)
        if player.max_jumps < 4:
            player.max_jumps += 1
        # Timer 5 secondes pour tuer les ennemis volants en les touchant
        player.jump_bonus_timer = 300  # 300 frames = 5 secondes à 60 FPS
        # Ne fait pas de dégâts au boss
    
    def _skip_round_intro(self):
        """Passe l'intro de manche et démarre la course immédiatement"""
        # Forcer immédiatement la transition vers la course
        self._round_intro_timer = 0  # Force la fin immédiatement
        # Réinitialiser les états
        self.match_manager.race_completed = False
        self.match_manager.rewards_shown = False
        self.match_manager.combat_completed = False
        self.match_manager.current_rewards = {
            "player1": {"coins": 0, "items": []},
            "player2": {"coins": 0, "items": []} if self.match_manager.game_mode in ["2v1", "pvp"] else None
        }
        # Démarrer la course immédiatement
        self.start_race()
        # Réinitialiser le flag pour permettre la détection de la nouvelle manche
        self._round_intro_last_rnd = -1
    
    def _transition_rewards_to_minigame(self):
        """Passe des récompenses au mini-jeu approprié selon la manche"""
        self.rewards_system.showing_rewards = False
        if self.match_manager.round_state == "match_complete":
            return
        
        # Déterminer quel mini-jeu démarrer selon la manche
        if self.match_manager.round_state == "minigame_morpion":
            self.tic_tac_toe_system.start_game()
        elif self.match_manager.round_state == "minigame_lava":
            self.lava_survival_system.start_game()
            self._lava_winner_handled = False  # Réinitialiser le flag quand on démarre le jeu
        elif self.match_manager.round_state == "combat":
            self.combat_system.start_combat(
                self.match_manager.current_rewards["player1"]["items"],
                self.match_manager.current_rewards["player2"]["items"] if self.match_manager.current_rewards.get("player2") else None
            )
    
    def _handle_minigame_winner(self, winner):
        """Gère le gagnant d'un mini-jeu et passe à la manche suivante"""
        # Si égalité (winner est None), passer quand même à la manche suivante sans points
        if winner is None:
            # Égalité = pas de points mais on continue quand même
            self.match_manager.combat_completed = True
            if self.match_manager.current_round < self.match_manager.num_rounds:
                self.match_manager.current_round += 1
                self.match_manager.round_state = "round_intro"
                self.match_manager.race_completed = False
                self.match_manager.rewards_shown = False
                self.match_manager.combat_completed = False
                self.match_manager.current_rewards = {
                    "player1": {"coins": 0, "items": []},
                    "player2": {"coins": 0, "items": []} if self.match_manager.game_mode in ["2v1", "pvp"] else None
                }
            else:
                self.match_manager.round_state = "match_complete"
            return
        
        if self.match_manager.game_mode == "1v1":
            save_joueur_vs_bot_progress(
                self.match_manager.current_round,
                self.match_manager.num_rounds,
                self.match_manager.player1_wins,
                self.match_manager.bot_wins,
                match_complete=self.match_manager.is_match_complete()
            )
        
        # Enregistrer la victoire (5 points)
        print(f"[DEBUG] _handle_minigame_winner appelé avec winner={winner}, current_round={self.match_manager.current_round}")
        try:
            self.match_manager.complete_combat(winner)
            print(f"[DEBUG] Après complete_combat: current_round={self.match_manager.current_round}, round_state={self.match_manager.round_state}")
        except Exception as e:
            print(f"[ERROR] Erreur dans complete_combat: {e}")
            import traceback
            traceback.print_exc()
            # En cas d'erreur, forcer la transition vers la manche suivante
            if self.match_manager.current_round < self.match_manager.num_rounds:
                self.match_manager.current_round += 1
                self.match_manager.round_state = "round_intro"
                print(f"[DEBUG] Transition forcée après erreur: current_round={self.match_manager.current_round}, round_state={self.match_manager.round_state}")
        
        # Vérifier si le match est terminé
        if self.match_manager.is_match_complete():
            print(f"[DEBUG] Match terminé, passage à match_complete")
            self.state = "match_complete"
        else:
            print(f"[DEBUG] Match non terminé, current_round={self.match_manager.current_round}, round_state={self.match_manager.round_state}, sera géré dans update_competitive")
            # S'assurer que round_state est bien "round_intro" pour la prochaine manche
            if self.match_manager.round_state != "round_intro" and self.match_manager.current_round <= self.match_manager.num_rounds:
                print(f"[DEBUG] Correction: round_state devrait être 'round_intro', mais c'est '{self.match_manager.round_state}'. Correction...")
                self.match_manager.round_state = "round_intro"
        # IMPORTANT: Ne pas changer self.state ici sauf si match_complete, laisser update_competitive gérer la transition
    
    def start_race(self):
        """Démarre une course - niveau = manche (progression)"""
        if self.match_manager and self.match_manager.game_mode == "pvp":
            # JvJ: MÊME NIVEAU pour les deux joueurs, niveau = manche (progression)
            # Manche 1 = Niveau 1, Manche 2 = Niveau 2, ... Dernière = Boss
            level_id = min(self.match_manager.current_round - 1, 4)
            if self.match_manager.current_round == self.match_manager.num_rounds:
                level_id = 4  # Dernière manche = boss
            self.level = Level(level_file=None, level_id=level_id)
            self.level2 = self.level  # Même niveau partagé
            self.player = Player(50, 100, player_id=1)
            self.player2 = Player(50, 100, player_id=2)
            
            # Manche 5 : boost de vitesse pour les joueurs
            if self.match_manager and self.match_manager.current_round == 5:
                self.player.boss_level_speed_boost = True
                self.player2.boss_level_speed_boost = True
            else:
                self.player.boss_level_speed_boost = False
                self.player2.boss_level_speed_boost = False
                # Réinitialiser les boucliers pour les autres manches
                self.player.ground_shield_timer = 0
                self.player.flying_shield_timer = 0
                self.player2.ground_shield_timer = 0
                self.player2.flying_shield_timer = 0
        else:
            # Niveau = manche : Manche 1 = Niveau 1, Manche 2 = Niveau 2, ... Dernière = Boss
            level_id = min(self.match_manager.current_round - 1, 4)
            if self.match_manager.current_round == self.match_manager.num_rounds:
                level_id = 4  # Dernière manche = boss
            self.current_level_id = level_id
            self.level = Level(level_file=None, level_id=level_id)
            self.level2 = None
            self.player = Player(50, 100, player_id=1)
            self.player2 = None
            if self.match_manager and self.match_manager.game_mode == "2v1":
                self.player2 = Player(100, 100, player_id=2)
            
            # Manche 5 : boost de vitesse pour le joueur
            if self.match_manager and self.match_manager.current_round == 5:
                self.player.boss_level_speed_boost = True
                if self.player2:
                    self.player2.boss_level_speed_boost = True
            else:
                self.player.boss_level_speed_boost = False
                if self.player2:
                    self.player2.boss_level_speed_boost = False
                # Réinitialiser le pouvoir de kill pour les autres manches
                self.player.can_kill_ground_enemies = False
                if self.player2:
                    self.player2.can_kill_ground_enemies = False
        self.race_system.start_race()
        # Toujours mettre round_state à "race" après avoir démarré la course
        self.match_manager.round_state = "race"
        # Réinitialiser le flag de sauvegarde du score pour le nouveau match
        self._score_saved = False
        # Afficher "Manche X" au début de chaque course (MAX 3 secondes)
        # Si on vient de skip l'intro, le timer est déjà à 0, sinon on affiche l'overlay
        if getattr(self, '_race_intro_timer', 0) == 0:
            # Si le timer est à 0 (skip), ne pas remettre à 180
            self._race_intro_timer = 0
        else:
            # Sinon, afficher l'overlay "Manche X" pendant MAX 3 secondes
            self._race_intro_timer = 180
        
        # Réinitialiser le flag d'explosion du boss
        self._boss_explosion_handled = False
        if hasattr(self, '_boss_explosion_timer'):
            delattr(self, '_boss_explosion_timer')
        
        # IMPORTANT: Pour la manche 5 (boss), ne pas initialiser le timer maintenant
        # Le timer sera initialisé seulement quand l'animation est terminée
        if self.level and self.level.level_type == "boss":
            # Ne pas initialiser boss_start_time ici, attendre la fin de l'animation
            # Le timer sera initialisé dans update_competitive quand _race_intro_timer atteint 0
            pass
    
    def handle_competitive_events(self, event):
        """Gère les événements en mode compétitif"""
        keys = pygame.key.get_pressed()
        
        if self.match_manager.round_state == "race":
            # Ne pas traiter les inputs tant que l'animation "Manche X" est affichée
            if getattr(self, '_race_intro_timer', 0) <= 0:
                self.handle_playing_events(event)
            # Saut Joueur 2: Clavier (I) OU Manette 2 (bouton X)
            if self.player2 and getattr(self, '_race_intro_timer', 0) <= 0:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                    self.player2.jump()
                    self.sound_manager.play_jump()  # Son de saut
                # Vérifier les manettes pour le joueur 2
                if event.type == pygame.JOYBUTTONDOWN:
                    # Méthode 1: Utiliser get_joy_for_player2()
                    joy2 = self.get_joy_for_player2()
                    if joy2 and event.joy == joy2.get_id() and event.button in (0, 2):
                        self.player2.jump()
                        self.sound_manager.play_jump()  # Son de saut
                    # Méthode 2: Vérifier directement avec player2_joy_id
                    elif self.player2_joy_id is not None and self.player2_joy_id != UNASSIGNED and event.joy == self.player2_joy_id and event.button in (0, 2):
                        self.player2.jump()
                        self.sound_manager.play_jump()  # Son de saut
            
            # Vérifier si la course est terminée (PvP: chacun son niveau) - uniquement quand on joue
            if getattr(self, '_race_intro_timer', 0) <= 0:
                # IMPORTANT: Vérifier le timeout AVANT de vérifier la victoire
                # Vérifier timeout boss (3min15) - défaite
                if self.level and self.level.level_type == "boss":
                    if self.level.check_boss_timeout():
                        # Temps écoulé = défaite (même si le boss n'a pas explosé) - capturer le temps écoulé
                        if hasattr(self.level, 'boss_start_time') and self.level.boss_start_time is not None:
                            elapsed_ms = pygame.time.get_ticks() - self.level.boss_start_time
                            elapsed_seconds = elapsed_ms / 1000.0
                            # Sauvegarder le temps écoulé (195 secondes = timeout)
                            self._boss_defeat_time = 195.0  # Temps maximum écoulé
                            print(f"[DEBUG] Timeout boss détecté, fin de partie - Temps écoulé: {elapsed_seconds:.2f}s")
                        else:
                            self._boss_defeat_time = 195.0  # Temps maximum par défaut
                        self.match_manager.round_state = "match_complete"
                        self.match_manager.match_lost = True  # Marquer comme perdu
                        self.sound_manager.play_defeat()  # Son de défaite
                        return
                    
                    # Vérifier si le boss explose OU si toutes les phases sont complétées (victoire)
                    # Le boss explose seulement si phase > 3 ET tous les ennemis tués
                    boss_won = False
                    if self.level.boss:
                        # Vérifier si le boss explose
                        if self.level.boss.exploding:
                            boss_won = True
                        # OU vérifier si toutes les phases sont complétées ET tous les ennemis tués
                        elif self.level.boss.phase > 3:
                            alive_enemies = [e for e in self.level.enemies if e.alive]
                            if len(alive_enemies) == 0:
                                # Forcer l'explosion si ce n'est pas déjà fait
                                self.level.boss.exploding = True
                                self.level.boss.explosion_timer = 0
                                self.level.boss.alive = False
                                boss_won = True
                    
                    if boss_won:
                        # Le boss est vaincu = victoire immédiate, passer à l'écran de fin
                        if not getattr(self, '_boss_explosion_handled', False):
                            self._boss_explosion_handled = True
                            # Sauvegarder le temps de victoire AVANT de finir la course
                            self._boss_victory_time = self.race_system.current_time
                            self.race_system.finish_race("player1")
                            if self.player2:
                                self.race_system.finish_race("player2")
                            print(f"[DEBUG] Boss vaincu en {self._boss_victory_time:.2f} secondes")
                            self.sound_manager.play_boss_explode()  # Son d'explosion du boss
                            self.sound_manager.play_victory()  # Son de victoire
                            # Attendre un peu pour voir l'explosion, puis passer à l'écran de fin
                            self._boss_explosion_timer = 180  # 3 secondes pour voir l'explosion
                
                # Si le timer d'explosion est actif, décrémenter et passer à la fin quand il atteint 0
                if hasattr(self, '_boss_explosion_timer') and self._boss_explosion_timer > 0:
                    self._boss_explosion_timer -= 1
                    if self._boss_explosion_timer <= 0:
                        # Passer à l'écran de fin avec le score
                        self.match_manager.round_state = "match_complete"
                        self.match_manager.match_lost = False  # Victoire !
                        # Sauvegarder automatiquement le score avec le temps du boss (seulement pour 1v1 et si le joueur a gagné)
                        if self.match_manager.game_mode == "1v1" and self.pseudo:
                            boss_time = getattr(self, '_boss_victory_time', None)
                            self.scoreboard.add_score(self.pseudo, self.match_manager.player1_score, boss_time)
                            print(f"[DEBUG] Score sauvegardé: {self.pseudo} - {self.match_manager.player1_score} pts - Temps boss: {boss_time}")
                        return
                
                if self.level and self.level.check_level_complete(self.player):
                    self.race_system.finish_race("player1")
                if self.player2:
                    lvl2 = self.level2 if self.match_manager.game_mode == "pvp" else self.level
                    if lvl2 and lvl2.check_level_complete(self.player2):
                        self.race_system.finish_race("player2")
                
                # Fin de course: 1v1 = J1 finit; pvp/2v1 = les deux ont fini
                race_done = False
                if self.match_manager.game_mode == "1v1":
                    race_done = self.race_system.player1_finished
                else:
                    race_done = self.race_system.player1_finished and (
                        self.race_system.player2_finished if self.player2 else True
                    )
                
                if race_done and not self.race_system.race_finished:
                    self.race_system.race_finished = True
                    p1_time = self.race_system.player1_time
                    p2_time = self.race_system.player2_time if self.player2 else None
                    bot_time = None
                    if self.match_manager.game_mode == "1v1":
                        bot_time = self.bot_ai.simulate_race_time(p1_time)
                        self.race_system.bot_time = bot_time
                    self.match_manager.complete_race(p1_time, p2_time, bot_time)
                    self.rewards_system.show_rewards()  # Affiche victoire (manche 5 = puis fin directe)
        
        elif self.match_manager.round_state == "rewards":
            # ESC : retour au menu (abandonner le match)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "menu"
            # Espace/Entrée : passer au combat/mini-jeu (sauf manche 4 qui passe automatiquement)
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                # Si manche 4, forcer la transition immédiate vers manche 5
                if self.match_manager.current_round == 4:
                    if self.rewards_system:
                        self.rewards_system.display_timer = self.rewards_system.display_duration
                        self.rewards_system.update()  # Force la transition
                else:
                    self.match_manager.show_rewards()
                    self._transition_rewards_to_minigame()
            # Manette : Bouton X ou Cercle = passer au combat (les 2 manettes)
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 1):  # X ou Cercle - les deux manettes peuvent passer
                    # Si manche 4, forcer la transition immédiate vers manche 5
                    if self.match_manager.current_round == 4:
                        if self.rewards_system:
                            self.rewards_system.display_timer = self.rewards_system.display_duration
                            self.rewards_system.update()  # Force la transition
                    else:
                        self.match_manager.show_rewards()
                        self._transition_rewards_to_minigame()
                elif event.button == 9 and self.settings.joystick_enabled:  # Options = retour
                    self.state = "menu"
        
        elif self.match_manager.round_state == "combat":
            # ESC : retour au menu (abandonner le match)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "menu"
            # Attaques pendant le combat - événements clavier
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Joueur 1 attaque
                    if self.combat_system:
                        self.combat_system.attack_player1()
                        self.sound_manager.play_combat_attack()  # Son d'attaque
                elif event.key == pygame.K_RETURN and self.match_manager.game_mode in ["pvp", "2v1"]:
                    # Joueur 2 attaque
                    if self.combat_system:
                        self.combat_system.attack_player2()
                        self.sound_manager.play_combat_attack()  # Son d'attaque
            # Manette : Bouton X (0) ou Cercle (1) = attaquer
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0 or event.button == 1:  # X ou Cercle
                    if self.combat_system:
                        # Déterminer quel joueur attaque selon la manette
                        try:
                            joy1 = self.get_joy_for_player1()
                            joy2 = self.get_joy_for_player2()
                            if joy1 and event.joy == joy1.get_id():
                                self.combat_system.attack_player1()
                                self.sound_manager.play_combat_attack()  # Son d'attaque
                            elif joy2 and event.joy == joy2.get_id() and self.match_manager.game_mode in ["pvp", "2v1"]:
                                self.combat_system.attack_player2()
                                self.sound_manager.play_combat_attack()  # Son d'attaque
                        except (AttributeError, pygame.error):
                            pass
        
        elif self.match_manager.round_state == "minigame_morpion":
            # ESC : retour au menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "menu"
            # Clic souris pour jouer
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.tic_tac_toe_system:
                    self.tic_tac_toe_system.handle_click(event.pos)
            # Clavier : Flèches pour naviguer, Espace/Entrée pour sélectionner
            elif event.type == pygame.KEYDOWN:
                if self.tic_tac_toe_system and not self.tic_tac_toe_system.game_over:
                    if event.key == pygame.K_UP:
                        self.tic_tac_toe_system.handle_controller_selection('up')
                    elif event.key == pygame.K_DOWN:
                        self.tic_tac_toe_system.handle_controller_selection('down')
                    elif event.key == pygame.K_LEFT:
                        self.tic_tac_toe_system.handle_controller_selection('left')
                    elif event.key == pygame.K_RIGHT:
                        self.tic_tac_toe_system.handle_controller_selection('right')
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.tic_tac_toe_system.handle_controller_selection('select')
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # Continuer après la fin (même en cas d'égalité)
                    if self.tic_tac_toe_system and self.tic_tac_toe_system.game_over:
                        winner = self.tic_tac_toe_system.get_winner_for_match()
                        self._handle_minigame_winner(winner)  # Gère aussi None (égalité)
            # Manette : D-Pad/Stick pour naviguer, X (0) pour sélectionner
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.tic_tac_toe_system:
                    if event.button == 0:  # X
                        if not self.tic_tac_toe_system.game_over:
                            self.tic_tac_toe_system.handle_controller_selection('select')
                        else:
                            # Continuer après la fin (même en cas d'égalité)
                            winner = self.tic_tac_toe_system.get_winner_for_match()
                            self._handle_minigame_winner(winner)  # Gère aussi None (égalité)
            elif event.type == pygame.JOYHATMOTION:
                # D-Pad pour naviguer
                if self.tic_tac_toe_system and not self.tic_tac_toe_system.game_over:
                    hat = event.value
                    if hat[0] == -1:  # Gauche
                        self.tic_tac_toe_system.handle_controller_selection('left')
                    elif hat[0] == 1:  # Droite
                        self.tic_tac_toe_system.handle_controller_selection('right')
                    elif hat[1] == 1:  # Haut
                        self.tic_tac_toe_system.handle_controller_selection('up')
                    elif hat[1] == -1:  # Bas
                        self.tic_tac_toe_system.handle_controller_selection('down')
            elif event.type == pygame.JOYAXISMOTION:
                # Stick analogique pour naviguer (seulement si mouvement significatif et avec debounce)
                if self.tic_tac_toe_system and not self.tic_tac_toe_system.game_over:
                    # Debounce pour éviter les mouvements trop rapides
                    current_time = pygame.time.get_ticks()
                    if not hasattr(self, '_last_axis_move_time'):
                        self._last_axis_move_time = {}
                    axis_key = f"{event.joy}_{event.axis}"
                    if axis_key not in self._last_axis_move_time:
                        self._last_axis_move_time[axis_key] = 0
                    
                    if current_time - self._last_axis_move_time[axis_key] > 200:  # 200ms entre chaque mouvement
                        if event.axis == 0:  # Stick horizontal
                            if event.value < -0.5:  # Gauche
                                self.tic_tac_toe_system.handle_controller_selection('left')
                                self._last_axis_move_time[axis_key] = current_time
                            elif event.value > 0.5:  # Droite
                                self.tic_tac_toe_system.handle_controller_selection('right')
                                self._last_axis_move_time[axis_key] = current_time
                        elif event.axis == 1:  # Stick vertical
                            if event.value < -0.5:  # Haut
                                self.tic_tac_toe_system.handle_controller_selection('up')
                                self._last_axis_move_time[axis_key] = current_time
                            elif event.value > 0.5:  # Bas
                                self.tic_tac_toe_system.handle_controller_selection('down')
                                self._last_axis_move_time[axis_key] = current_time
        
        elif self.match_manager.round_state == "minigame_lava":
            # ESC : retour au menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "menu"
            # Saut joueur 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.lava_survival_system and not self.lava_survival_system.game_over:
                    self.lava_survival_system.player1_jump_pressed = True
                elif self.lava_survival_system and self.lava_survival_system.game_over and not getattr(self, '_lava_winner_handled', False):
                    winner = self.lava_survival_system.get_winner_for_match()
                    self._lava_winner_handled = True  # Marquer comme géré pour éviter les appels multiples
                    self._handle_minigame_winner(winner)  # Gère aussi None
            # Saut joueur 2 (PvP)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                if self.lava_survival_system and not self.lava_survival_system.game_over:
                    self.lava_survival_system.player2_jump_pressed = True
            # Manette : Saut
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0 or event.button == 2:  # X ou Carré
                    try:
                        joy1 = self.get_joy_for_player1()
                        joy2 = self.get_joy_for_player2()
                        if joy1 and event.joy == joy1.get_id():
                            if self.lava_survival_system and not self.lava_survival_system.game_over:
                                self.lava_survival_system.player1_jump_pressed = True
                        elif joy2 and event.joy == joy2.get_id() and self.match_manager.game_mode == "pvp":
                            if self.lava_survival_system and not self.lava_survival_system.game_over:
                                self.lava_survival_system.player2_jump_pressed = True
                    except (AttributeError, pygame.error):
                        pass
                elif event.button == 1:  # Cercle - continuer après la fin
                    if self.lava_survival_system and self.lava_survival_system.game_over and not getattr(self, '_lava_winner_handled', False):
                        winner = self.lava_survival_system.get_winner_for_match()
                        self._lava_winner_handled = True  # Marquer comme géré pour éviter les appels multiples
                        self._handle_minigame_winner(winner)  # Gère aussi None
        
        elif self.match_manager.round_state == "round_intro":
            # Espace/Entrée ou manette : passer à la course
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                self._skip_round_intro()
            elif event.type == pygame.JOYBUTTONDOWN and event.button in (0, 1):
                self._skip_round_intro()
        
        elif self.match_manager.round_state == "match_complete":
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                self.state = "menu"
    
    def draw_mode_selection(self):
        """Dessine l'écran de sélection de mode"""
        from config import GRADIENT_START, GRADIENT_END
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        self.game_modes.draw_mode_selection(self.screen, self.mode_selection_index)
    
    def draw_submenu(self, title, options, selected_index, back_hint=True):
        """Dessine un sous-menu générique"""
        from config import GRADIENT_START, GRADIENT_END
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        title_text = self.font_large.render(title, True, ORANGE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        y_start = 250
        for i, opt in enumerate(options):
            color = YELLOW if i == selected_index else WHITE
            text = self.font_medium.render(opt, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 70))
            if i == selected_index:
                pygame.draw.rect(self.screen, (0, 0, 0, 100),
                    (rect.left - 20, rect.top - 10, rect.width + 40, rect.height + 20))
            self.screen.blit(text, rect)
        
        if back_hint:
            hint = self.font_small.render("ESC pour retourner", True, GRAY)
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))
    
    def draw_course_combat_choice(self):
        """Sous-menu Course et Combat: Course seule ou Combat seul"""
        self.draw_submenu("Course et Combat", self.course_combat_options, self.course_combat_index)
    
    def draw_course_choice(self):
        """Choix de la course: Parcours 1, 2 ou Boss"""
        self.draw_submenu("Choisir une course", self.course_options, self.course_choice_index)
    
    def draw_combat_choice(self):
        """Choix du combat: vs Joueur ou vs Bot"""
        self.draw_submenu("Choisir un combat", self.combat_options, self.combat_choice_index)
    
    def draw_course_only(self):
        """Dessine la course seule (sans combat)"""
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
        
        if self.course_only_completed:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            t = self.font_large.render("Course terminée!", True, GREEN)
            self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            h = self.font_small.render("Entrée ou ESPACE pour retourner au menu", True, GRAY)
            self.screen.blit(h, (SCREEN_WIDTH // 2 - h.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        else:
            score_text = self.font_medium.render(f"Score: {self.score} | Vies: {self.player.lives}", True, WHITE)
            self.screen.blit(score_text, (20, 20))
    
    def draw_combat_only(self):
        """Dessine le combat seul"""
        if self.combat_system:
            self.combat_system.draw(self.screen)
        if self.combat_only_mode and hasattr(self, '_combat_only_winner') and self._combat_only_winner:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            w = self._combat_only_winner
            t = self.font_large.render(f"Combat terminé! Gagnant: {w}", True, GREEN)
            self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            h = self.font_small.render("Entrée ou ESPACE pour retourner au menu", True, GRAY)
            self.screen.blit(h, (SCREEN_WIDTH // 2 - h.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    
    def handle_course_combat_choice_events(self, event):
        """Gère les événements du sous-menu Course et Combat"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.course_combat_index = (self.course_combat_index - 1) % len(self.course_combat_options)
            elif event.key == pygame.K_DOWN:
                self.course_combat_index = (self.course_combat_index + 1) % len(self.course_combat_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_course_combat_option()
            elif event.key == pygame.K_ESCAPE:
                self.state = "mode_selection"
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                if event.type == pygame.JOYHATMOTION and self.joystick.get_numhats() > 0:
                    hat = self.joystick.get_hat(0)
                    if hat[1] == 1:
                        self.course_combat_index = (self.course_combat_index - 1) % len(self.course_combat_options)
                    elif hat[1] == -1:
                        self.course_combat_index = (self.course_combat_index + 1) % len(self.course_combat_options)
                elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    self._select_course_combat_option()
            except (AttributeError, IndexError):
                pass
    
    def _select_course_combat_option(self):
        if self.course_combat_options[self.course_combat_index] == "Course seule":
            self.state = "course_choice"
            self.course_choice_index = 0
        else:
            self.state = "combat_choice"
            self.combat_choice_index = 0
    
    def handle_course_choice_events(self, event):
        """Gère le choix de la course"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.course_choice_index = (self.course_choice_index - 1) % len(self.course_options)
            elif event.key == pygame.K_DOWN:
                self.course_choice_index = (self.course_choice_index + 1) % len(self.course_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._start_course_only()
            elif event.key == pygame.K_ESCAPE:
                self.state = "course_combat_choice"
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                if event.type == pygame.JOYHATMOTION and self.joystick.get_numhats() > 0:
                    hat = self.joystick.get_hat(0)
                    if hat[1] == 1:
                        self.course_choice_index = (self.course_choice_index - 1) % len(self.course_options)
                    elif hat[1] == -1:
                        self.course_choice_index = (self.course_choice_index + 1) % len(self.course_options)
                elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    self._start_course_only()
            except (AttributeError, IndexError):
                pass
    
    def _start_course_only(self):
        level_id = self.course_choice_index
        self.state = "course_only"
        self.course_only_completed = False
        self.level = Level(level_file=None, level_id=level_id)
        self.player = Player(50, 100)
        self.score = 0
        self.camera_x = 0
    
    def handle_combat_choice_events(self, event):
        """Gère le choix du combat (vs Joueur ou vs Bot)"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.combat_choice_index = (self.combat_choice_index - 1) % len(self.combat_options)
            elif event.key == pygame.K_DOWN:
                self.combat_choice_index = (self.combat_choice_index + 1) % len(self.combat_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._start_combat_only()
            elif event.key == pygame.K_ESCAPE:
                self.state = "course_combat_choice"
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                if event.type == pygame.JOYHATMOTION and self.joystick.get_numhats() > 0:
                    hat = self.joystick.get_hat(0)
                    if hat[1] == 1:
                        self.combat_choice_index = (self.combat_choice_index - 1) % len(self.combat_options)
                    elif hat[1] == -1:
                        self.combat_choice_index = (self.combat_choice_index + 1) % len(self.combat_options)
                elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    self._start_combat_only()
            except (AttributeError, IndexError):
                pass
    
    def _start_combat_only(self):
        mode_key = "pvp" if self.combat_choice_index == 0 else "1v1"
        self.combat_only_mode = True
        self._combat_only_winner = None
        self.match_manager = MatchManager(mode_key, 1)
        self.match_manager.start_match()
        self.match_manager.round_state = "combat"
        self.combat_system = CombatSystem(self.match_manager)
        self.combat_system.start_combat([], [] if mode_key == "pvp" else None)
        self.state = "combat_only"
    
    def handle_course_only_events(self, event):
        """Gère les événements pendant la course seule"""
        if self.course_only_completed:
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE):
                self.state = "menu"
        else:
            self.handle_playing_events(event)
    
    def handle_combat_only_events(self, event):
        """Gère les événements pendant le combat seul"""
        if self._combat_only_winner:
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE):
                self.combat_only_mode = False
                self.state = "menu"
    
    def update_course_only(self):
        """Met à jour la course seule"""
        if self.course_only_completed:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        elif keys[pygame.K_RIGHT]:
            self.player.move_right()
        if self.joystick_available and self.settings.joystick_enabled and self.joystick:
            try:
                axis_x = self.joystick.get_axis(0)
                if axis_x < -0.3:
                    self.player.move_left()
                elif axis_x > 0.3:
                    self.player.move_right()
            except (AttributeError, IndexError, pygame.error):
                pass
        self.player.update(self.level.platforms)
        self.level.update(self.player)
        for c in self.level.collectibles:
            if c.check_collision(self.player):
                if getattr(c, 'collect_type', 'speed') == 'speed':
                    self.player.stars_collected += 1
                else:
                    self._apply_jump_bonus(self.player)
        if self.level.level_type == "boss" and hasattr(self.level, 'bounds_x'):
            self.player.rect.x = max(self.level.bounds_x[0], min(self.player.rect.x, self.level.bounds_x[1] - self.player.rect.width))
        for e in self.level.enemies:
            col, crushed = e.check_collision_with_player(self.player)
            if col:
                if crushed:
                    e.alive = False
                    self.sound_manager.play_enemy_kill()  # Son de mort d'ennemi
                else:
                    self.player.lives -= 1
                    self.sound_manager.play_player_hit()  # Son quand le joueur est touché
                    if self.player.lives > 0:
                        self.player.reset_to_checkpoint()
                    else:
                        self.course_only_completed = True
        if self.level.boss:
            col, crushed = self.level.boss.check_collision_with_player(self.player)
            if col:
                if crushed:
                    self.level.boss.take_damage()
                    self.score += SCORE_ENEMY * 2
                    self.player.velocity_y = PLAYER_JUMP_STRENGTH * 0.7
                else:
                    self.player.lives -= 1
                    if self.player.lives > 0:
                        self.player.reset_to_checkpoint()
                    else:
                        self.course_only_completed = True
        if self.level.check_level_complete(self.player):
            self.course_only_completed = True
    
    def update_combat_only(self):
        """Met à jour le combat seul"""
        if self._combat_only_winner:
            return
        keys = pygame.key.get_pressed()
        player2_keys = keys if self.match_manager and self.match_manager.game_mode == "pvp" else None
        try:
            joy1 = self.get_joy_for_player1()
            p1_attack = joy1 and (joy1.get_button(0) or joy1.get_button(2))
        except (AttributeError, pygame.error):
            p1_attack = False
        try:
            joy2 = self.get_joy_for_player2()
            p2_attack = joy2 and (joy2.get_button(0) or joy2.get_button(2))
        except (AttributeError, pygame.error):
            p2_attack = False
        winner = self.combat_system.update(keys, player2_keys, player1_attack=p1_attack, player2_attack=p2_attack)
        if winner:
            self._combat_only_winner = {"player1": "Joueur 1", "player2": "Joueur 2", "bot": "Bot"}.get(winner, winner)
    
    def draw_competitive_mode(self):
        """Dessine le mode compétitif"""
        if self.match_manager.round_state == "race":
            self.background.update()
            
            # Mode PvP : Split-screen avec deux joueurs
            if self.match_manager.game_mode == "pvp":
                # S'assurer que player2 et level2 existent
                if not self.player2:
                    print(f"[DEBUG] Erreur: player2 n'existe pas en mode PvP! Création...")
                    self.player2 = Player(50, 100, player_id=2)
                if not self.level2:
                    print(f"[DEBUG] Erreur: level2 n'existe pas en mode PvP! Création...")
                    if self.level:
                        self.level2 = self.level
                    else:
                        level_id = min(self.match_manager.current_round - 1, 4)
                        if self.match_manager.current_round == self.match_manager.num_rounds:
                            level_id = 4
                        self.level2 = Level(level_file=None, level_id=level_id)
                        self.level = self.level2
                
                if self.player2 and self.level2:
                    # ÉCRAN PARTAGÉ: DEUX MONDES DIFFÉRENTS - J1 à gauche, J2 à droite
                    half_w = SCREEN_WIDTH // 2
                    # Monde 1 - Joueur 1 (Parcours 1 ou 2)
                    cam1 = self.player.rect.centerx - half_w // 2
                    cam1 = max(0, min(cam1, (self.level.end_x + 100) - half_w))
                    surf1 = self.screen.subsurface((0, 0, half_w, SCREEN_HEIGHT))
                    self.background.draw(surf1)
                    self.level.draw(surf1, camera_x=cam1)
                    old_x = self.player.rect.x
                    self.player.rect.x -= cam1
                    self.player.draw(surf1)
                    self.player.rect.x = old_x
                    # Tint bleu pour J1 (champ gauche)
                    tint1 = pygame.Surface((half_w, SCREEN_HEIGHT))
                    tint1.set_alpha(25)
                    tint1.fill(BLUE)
                    surf1.blit(tint1, (0, 0))
                    # Monde 2 - Joueur 2 (l'autre niveau)
                    cam2 = self.player2.rect.centerx - half_w // 2
                    cam2 = max(0, min(cam2, (self.level2.end_x + 100) - half_w))
                    surf2 = self.screen.subsurface((half_w, 0, half_w, SCREEN_HEIGHT))
                    self.background.draw(surf2)
                    self.level2.draw(surf2, camera_x=cam2)
                    old_x2 = self.player2.rect.x
                    self.player2.rect.x -= cam2
                    self.player2.draw(surf2)
                    self.player2.rect.x = old_x2
                    # Tint vert pour J2 (champ droit)
                    tint2 = pygame.Surface((half_w, SCREEN_HEIGHT))
                    tint2.set_alpha(25)
                    tint2.fill(GREEN)
                    surf2.blit(tint2, (0, 0))
                    pygame.draw.line(self.screen, WHITE, (half_w, 0), (half_w, SCREEN_HEIGHT), 2)
                    font_s = pygame.font.Font(None, 24)
                    self.screen.blit(font_s.render("J1", True, BLUE), (10, 10))
                    self.screen.blit(font_s.render("J2", True, GREEN), (half_w + 10, 10))
            elif self.match_manager.game_mode == "2v1" and self.player2:
                # 2v1: MÊME NIVEAU - les deux joueurs visibles, caméra au centre
                center_x = (self.player.rect.centerx + self.player2.rect.centerx) // 2
                self.camera_x = center_x - SCREEN_WIDTH // 2
                max_cam = max(0, (self.level.end_x + 100) - SCREEN_WIDTH)
                self.camera_x = max(0, min(self.camera_x, max_cam))
                self.background.draw(self.screen)
                self.level.draw(self.screen, camera_x=self.camera_x)
                old_x1, old_x2 = self.player.rect.x, self.player2.rect.x
                self.player.rect.x -= self.camera_x
                self.player2.rect.x -= self.camera_x
                self.player.draw(self.screen)
                self.player2.draw(self.screen)
                self.player.rect.x, self.player2.rect.x = old_x1, old_x2
            else:
                # 1v1: vue normale
                if self.player and self.level:
                    self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
                    max_camera_x = max(0, (self.level.end_x + 100) - SCREEN_WIDTH)
                    self.camera_x = max(0, min(self.camera_x, max_camera_x))
                self.background.draw(self.screen)
                if self.level:
                    self.level.draw(self.screen, camera_x=self.camera_x)
                if self.player:
                    old_x = self.player.rect.x
                    self.player.rect.x -= self.camera_x
                    self.player.draw(self.screen)
                    self.player.rect.x = old_x
            
            self.race_system.update()
            self.race_system.draw_race_hud(self.screen, self.match_manager, self.player, self.level)
            
            # Overlay "Manche X" au début de chaque course (Manche 2, 3, 4, Dernière)
            if getattr(self, '_race_intro_timer', 0) > 0:
                self._draw_race_intro_overlay()
            
        elif self.match_manager.round_state == "rewards":
            # Dessiner les récompenses
            # NOTE: update() est déjà appelé dans update_competitive(), ne pas le refaire ici
            # Vérifier que showing_rewards est True avant de dessiner
            if self.rewards_system and self.rewards_system.showing_rewards and self.match_manager.round_state == "rewards":
                self.rewards_system.draw(self.screen)
            # Si round_state a changé à round_intro (transition manche 4->5), dessiner round_intro
            if self.match_manager.round_state == "round_intro":
                self.draw_round_intro()
        
        elif self.match_manager.round_state == "combat":
            self.combat_system.draw(self.screen)
        
        elif self.match_manager.round_state == "minigame_morpion":
            if self.tic_tac_toe_system:
                self.tic_tac_toe_system.draw(self.screen)
        
        elif self.match_manager.round_state == "minigame_lava":
            if self.lava_survival_system:
                self.lava_survival_system.draw(self.screen)
        
        elif self.match_manager.round_state == "round_intro":
            self.draw_round_intro()
        
        elif self.match_manager.round_state == "match_complete":
            # Dessiner l'écran de fin de match
            self.draw_match_complete()
    
    def _draw_race_intro_overlay(self):
        """Overlay Manche X au début de chaque course (semi-transparent)"""
        alpha = min(255, int(255 * getattr(self, '_race_intro_timer', 0) / 180))
        if alpha <= 0:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        rnd = self.match_manager.current_round
        total = self.match_manager.num_rounds
        font_huge = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        if rnd == total:
            title = font_huge.render("DERNIÈRE MANCHE", True, YELLOW)
            sub = font_medium.render("Contre le Boss !", True, RED)
        else:
            title = font_huge.render(f"MANCHE {rnd}", True, YELLOW)
            sub = font_medium.render("Préparez-vous...", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 320))
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 400))
    
    def draw_round_intro(self):
        """Animation Manche X ou Dernière manche - Contre le boss (fond dégradé violet, effet bounce)"""
        from config import GRADIENT_START, GRADIENT_END
        # Fond dégradé violet
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            self.screen.fill((r, g, b), (0, y, SCREEN_WIDTH, 1))
        
        rnd = self.match_manager.current_round
        total = self.match_manager.num_rounds
        timer = getattr(self, '_round_intro_timer', 0)
        # Effet bounce sur le texte
        bounce = abs(((timer / 15) % 2) - 1) * 0.2 + 1
        font_size = int(72 * bounce)
        font_huge = pygame.font.Font(None, max(48, font_size))
        font_medium = pygame.font.Font(None, 36)
        
        if rnd == total:
            title = font_huge.render("DERNIÈRE MANCHE", True, YELLOW)
            sub = font_medium.render("Contre le Boss !", True, RED)
        else:
            title = font_huge.render(f"MANCHE {rnd}", True, YELLOW)
            sub = font_medium.render("Préparez-vous...", True, WHITE)
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 280))
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 380))
        
        hint = pygame.font.Font(None, 24).render("Espace/Entrée ou X/Cercle : Continuer", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))
    
    def draw_match_complete(self):
        """Dessine l'écran de fin de match"""
        self.screen.fill(BLACK)
        
        font_large = pygame.font.Font(None, 56)
        font_medium = pygame.font.Font(None, 36)
        
        # Vérifier si le joueur a perdu (timeout boss)
        if getattr(self.match_manager, 'match_lost', False):
            title = font_large.render("VOUS AVEZ PERDU!", True, RED)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
            reason = font_medium.render("Temps écoulé (3min15) - Tous les ennemis n'ont pas été tués", True, YELLOW)
            self.screen.blit(reason, (SCREEN_WIDTH // 2 - reason.get_width() // 2, 200))
        else:
            winner = self.match_manager.get_match_winner()
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
        
        # Scores finaux (points course + combat)
        y_offset = 300
        scores = [f"Joueur 1: {self.match_manager.player1_score} points"]
        if self.match_manager.game_mode == "pvp":
            scores.append(f"Joueur 2: {self.match_manager.player2_score} points")
        elif self.match_manager.game_mode == "2v1":
            scores.append(f"Joueur 2: {self.match_manager.player2_score} points")
            scores.append(f"Bot: {self.match_manager.bot_score} points")
            scores.append(f"Équipe: {self.match_manager.player1_score + self.match_manager.player2_score} pts")
        else:
            scores.append(f"Bot: {self.match_manager.bot_score} points")
        
        # Afficher le temps (victoire ou défaite)
        if getattr(self.match_manager, 'match_lost', False):
            # Défaite : afficher le temps écoulé
            defeat_time = getattr(self, '_boss_defeat_time', 195.0)
            time_minutes = int(defeat_time // 60)
            time_seconds = int(defeat_time % 60)
            time_milliseconds = int((defeat_time % 1) * 1000)
            time_text = font_medium.render(
                f"⏱ Temps écoulé: {time_minutes:02d}:{time_seconds:02d}.{time_milliseconds:03d}",
                True, RED
            )
            self.screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, y_offset))
            y_offset += 50
        elif hasattr(self, '_boss_victory_time') and self._boss_victory_time is not None:
            # Victoire : afficher le temps pour vaincre le boss
            time_minutes = int(self._boss_victory_time // 60)
            time_seconds = int(self._boss_victory_time % 60)
            time_milliseconds = int((self._boss_victory_time % 1) * 1000)
            time_text = font_medium.render(
                f"⏱ Temps pour vaincre le boss: {time_minutes:02d}:{time_seconds:02d}.{time_milliseconds:03d}",
                True, YELLOW
            )
            self.screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, y_offset))
            y_offset += 50
        
        for score in scores:
            text = font_medium.render(score, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 50
        
        # Afficher le rang du joueur dans le classement (si mode 1v1 et pseudo défini)
        if self.match_manager.game_mode == "1v1" and self.pseudo:
            # Déterminer le temps à utiliser pour le classement
            if getattr(self.match_manager, 'match_lost', False):
                # Défaite : utiliser le temps écoulé (timeout)
                boss_time = getattr(self, '_boss_defeat_time', 195.0)
            else:
                # Victoire : utiliser le temps de victoire
                boss_time = getattr(self, '_boss_victory_time', None)
            
            player_rank = self.scoreboard.get_rank(
                self.match_manager.player1_score,
                boss_time
            )
            if player_rank:
                rank_text = font_medium.render(f"🏆 Votre classement: #{player_rank}", True, CYAN)
                self.screen.blit(rank_text, (SCREEN_WIDTH // 2 - rank_text.get_width() // 2, y_offset))
                y_offset += 50
        
        # Instructions
        inst = self.font_small.render("Appuyez sur Entrée ou ESC pour retourner au menu", True, GRAY)
        self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def run(self):
        """Boucle principale du jeu"""
        # Ignorer les événements initiaux de la manette pour éviter le démarrage automatique
        pygame.event.clear()
        
        print("[DEBUG] Démarrage de la boucle principale du jeu...")
        print("[DEBUG] Démarrage de la boucle principale du jeu...")
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    # Capture d'écran intégrée (F12) - fonctionne même en plein écran
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                        self._take_screenshot()
                    
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
                    elif self.state == "enter_name" or self.state == "enter_name_before_match":
                        self.handle_name_input_events(event)
                    elif self.state == "scoreboard":
                        self.handle_scoreboard_events(event)
                    elif self.state == "mode_selection":
                        self.handle_mode_selection_events(event)
                    elif self.state == "player_selection":
                        self.handle_player_selection_events(event)
                    elif self.state == "course_combat_choice":
                        self.handle_course_combat_choice_events(event)
                    elif self.state == "course_choice":
                        self.handle_course_choice_events(event)
                    elif self.state == "combat_choice":
                        self.handle_combat_choice_events(event)
                    elif self.state == "course_only":
                        self.handle_course_only_events(event)
                    elif self.state == "combat_only":
                        self.handle_combat_only_events(event)
                    elif self.state == "competitive":
                        self.handle_competitive_events(event)
                
                if not self.running:
                    break
                
                # Mettre à jour le jeu
                try:
                    if self.state == "player_selection":
                        self.update_player_selection()
                    elif self.state == "competitive":
                        self.update_competitive()
                    elif self.state == "course_only":
                        self.update_course_only()
                    elif self.state == "combat_only":
                        self.update_combat_only()
                    else:
                        self.update_game()
                except Exception as e:
                    print(f"[ERROR] Erreur dans update: {e}")
                    import traceback
                    traceback.print_exc()
                    # Ne pas quitter le jeu, juste continuer
                
                # Dessiner
                try:
                    self.draw_game()
                except Exception as e:
                    print(f"[ERROR] Erreur dans draw_game: {e}")
                    import traceback
                    traceback.print_exc()
                    # Ne pas quitter le jeu, juste continuer
                
                # Contrôler le FPS
                self.clock.tick(FPS)
        except KeyboardInterrupt:
            print("[DEBUG] Interruption clavier détectée")
            self.running = False
        except Exception as e:
            print(f"[ERROR] Erreur fatale dans la boucle principale: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("[DEBUG] Fermeture du jeu...")
            pygame.quit()
            import sys
            sys.exit(0)

