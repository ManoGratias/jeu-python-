"""
Système "Le Sol est en Lave" - Mini-jeu après manche 3
Survie verticale : les plateformes montent, le joueur doit rester en haut
Le gagnant remporte 5 points
"""
import pygame
import random
from config import *

class LavaSurvivalSystem:
    def __init__(self, match_manager):
        self.match_manager = match_manager
        self.game_active = False
        self.scroll_speed = 1  # Pixels par frame (le sol monte)
        
        # Joueurs
        self.player1_y = SCREEN_HEIGHT - 200
        self.player2_y = SCREEN_HEIGHT - 200
        self.player1_x = SCREEN_WIDTH // 3
        self.player2_x = SCREEN_WIDTH * 2 // 3
        self.player1_velocity_y = 0
        self.player2_velocity_y = 0
        self.player1_on_platform = False
        self.player2_on_platform = False
        # Compteurs de sauts (max 2)
        self.player1_jump_count = 0
        self.player2_jump_count = 0
        
        # Bot (pour mode 1v1 et 2v1)
        self.bot_y = SCREEN_HEIGHT - 200
        self.bot_x = SCREEN_WIDTH // 2
        self.bot_velocity_y = 0
        self.bot_on_platform = False
        self.bot_jump_count = 0
        self.bot_jump_cooldown = 0  # Cooldown pour éviter les sauts trop fréquents
        
        # Plateformes (liste de (x, y, width))
        self.platforms = []
        self.platform_height = 20
        self.platform_width = 100
        
        # État
        self.winner = None
        self.game_over = False
        self.player1_jump_pressed = False
        self.player2_jump_pressed = False
        self.survival_timer = 0
        self.survival_time_limit = 30  # 30 secondes pour gagner en survivant
        
    def start_game(self):
        """Démarre une nouvelle partie"""
        self.game_active = True
        self.game_over = False
        self.winner = None
        self.scroll_speed = 1
        self.survival_timer = 0  # Réinitialiser le timer de survie
        self.player1_jump_pressed = False
        self.player2_jump_pressed = False
        
        # Position initiale des joueurs
        self.player1_y = SCREEN_HEIGHT - 200
        self.player2_y = SCREEN_HEIGHT - 200
        self.player1_x = SCREEN_WIDTH // 3
        self.player2_x = SCREEN_WIDTH * 2 // 3
        self.player1_velocity_y = 0
        self.player2_velocity_y = 0
        self.player1_on_platform = False
        self.player2_on_platform = False
        # Réinitialiser les compteurs de sauts
        self.player1_jump_count = 0
        self.player2_jump_count = 0
        
        # Position initiale du bot
        self.bot_y = SCREEN_HEIGHT - 200
        self.bot_x = SCREEN_WIDTH // 2
        self.bot_velocity_y = 0
        self.bot_on_platform = False
        self.bot_jump_count = 0
        self.bot_jump_cooldown = 0
        
        # Créer des plateformes initiales (en haut de l'écran, elles vont descendre)
        self.platforms = []
        for i in range(8):
            x = random.randint(50, SCREEN_WIDTH - 150)
            y = 100 + i * 100  # Commencer en haut, elles descendent
            self.platforms.append((x, y, self.platform_width))
        
        # Plateformes pour les deux joueurs au départ (en bas)
        self.platforms.append((self.player1_x - 50, SCREEN_HEIGHT - 150, self.platform_width))
        self.platforms.append((self.player2_x - 50, SCREEN_HEIGHT - 150, self.platform_width))
    
    def update(self, player1_left=False, player1_right=False, player1_jump=False,
               player2_left=False, player2_right=False, player2_jump=False):
        """Met à jour le jeu"""
        if not self.game_active or self.game_over:
            return
        
        # Timer de survie
        self.survival_timer += 1/60  # Incrémenter chaque frame (60 FPS)
        
        # Faire DESCENDRE toutes les plateformes (vers le bas)
        self.platforms = [(x, y + self.scroll_speed, w) for x, y, w in self.platforms]
        
        # Ajouter de nouvelles plateformes en haut si nécessaire (elles descendent)
        if self.platforms and min(y for _, y, _ in self.platforms) > 50:
            x = random.randint(50, SCREEN_WIDTH - 150)
            self.platforms.append((x, -50, self.platform_width))
        
        # Supprimer les plateformes qui sont sorties en bas (trop bas)
        self.platforms = [(x, y, w) for x, y, w in self.platforms if y < SCREEN_HEIGHT + 100]
        
        # Mouvement joueur 1
        if player1_left:
            self.player1_x = max(30, self.player1_x - 5)
        if player1_right:
            self.player1_x = min(SCREEN_WIDTH - 30, self.player1_x + 5)
        # Saut joueur 1 (événement) - MAX 2 SAUTS
        if self.player1_jump_pressed:
            if self.player1_jump_count < 2:  # Limite à 2 sauts
                if self.player1_on_platform:
                    self.player1_velocity_y = -15  # Force de saut plus forte pour monter
                else:
                    self.player1_velocity_y = -8  # Petit saut en l'air
                self.player1_jump_count += 1
            self.player1_jump_pressed = False
        
        # Mouvement joueur 2 (si PvP)
        if self.match_manager.game_mode == "pvp":
            if player2_left:
                self.player2_x = max(30, self.player2_x - 5)
            if player2_right:
                self.player2_x = min(SCREEN_WIDTH - 30, self.player2_x + 5)
            # Saut joueur 2 (événement) - MAX 2 SAUTS
            if self.player2_jump_pressed:
                if self.player2_jump_count < 2:  # Limite à 2 sauts
                    if self.player2_on_platform:
                        self.player2_velocity_y = -15
                    else:
                        self.player2_velocity_y = -8
                    self.player2_jump_count += 1
                self.player2_jump_pressed = False
        
        # Physique : gravité (plus faible pour permettre de monter)
        self.player1_velocity_y += 0.4
        self.player2_velocity_y += 0.4
        
        # Appliquer la vélocité
        self.player1_y += self.player1_velocity_y
        self.player2_y += self.player2_velocity_y
        
        # Bot AI (pour mode 1v1 et 2v1)
        if self.match_manager.game_mode != "pvp":
            # Appliquer la gravité au bot AVANT de mettre à jour l'IA
            self.bot_velocity_y += 0.4
            self._update_bot()  # Met à jour la position et la vélocité du bot
            self.bot_y += self.bot_velocity_y  # Appliquer la vélocité mise à jour
        
        # Vérifier collision avec plateformes
        self._check_platform_collisions()
        
        # Vérifier si un joueur touche le bas (perdu) - la lave monte
        player1_lost = self.player1_y >= SCREEN_HEIGHT - 20
        player2_lost = self.match_manager.game_mode == "pvp" and self.player2_y >= SCREEN_HEIGHT - 20
        bot_lost = self.match_manager.game_mode != "pvp" and self.bot_y >= SCREEN_HEIGHT - 20
        
        # LE PREMIER QUI TOMBE PERD - CELUI QUI SURVIT GAGNE LES 5 POINTS
        if player1_lost:
            # Joueur 1 a perdu (premier à tomber)
            if self.match_manager.game_mode == "pvp":
                self.winner = 'player2'  # Joueur 2 survit et gagne
            else:
                self.winner = 'bot'  # Bot survit et gagne
            self.game_over = True
        elif player2_lost:
            # Joueur 2 a perdu (premier à tomber) - PvP uniquement
            self.winner = 'player1'  # Joueur 1 survit et gagne
            self.game_over = True
        elif bot_lost:
            # Bot a perdu (premier à tomber) - Mode 1v1 ou 2v1
            self.winner = 'player1'  # Joueur 1 survit et gagne
            self.game_over = True
        # Vérifier si le joueur survit assez longtemps (victoire par survie)
        elif self.survival_timer >= self.survival_time_limit:
            # Si personne n'est tombé après 30 secondes, celui qui est le plus haut gagne
            if self.match_manager.game_mode == "pvp":
                # En PvP, celui qui est le plus haut gagne
                if self.player1_y < self.player2_y:
                    self.winner = 'player1'
                else:
                    self.winner = 'player2'
            else:
                # Mode 1v1 ou 2v1 : comparer les positions
                if self.player1_y < self.bot_y:
                    self.winner = 'player1'  # Joueur plus haut = gagne
                else:
                    self.winner = 'bot'  # Bot plus haut = gagne
            self.game_over = True
    
    def _update_bot(self):
        """IA du bot : se comporte comme un joueur - se déplace et saute pour survivre"""
        # Le bot doit toujours essayer de monter pour éviter de tomber
        # Trouver la plateforme la plus proche au-dessus du bot (priorité aux plateformes hautes)
        nearest_platform_above = None
        min_distance_above = float('inf')
        nearest_y_above = float('inf')
        
        for px, py, pw in self.platforms:
            # Plateforme au-dessus du bot (avec une marge pour éviter de sauter trop tôt)
            if py < self.bot_y - 50:
                distance_x = abs(px + pw/2 - self.bot_x)
                # Prioriser les plateformes les plus hautes et les plus proches horizontalement
                if py < nearest_y_above or (py == nearest_y_above and distance_x < min_distance_above):
                    min_distance_above = distance_x
                    nearest_y_above = py
                    nearest_platform_above = (px, py, pw)
        
        # Si aucune plateforme au-dessus, chercher la plus proche horizontalement
        if not nearest_platform_above:
            for px, py, pw in self.platforms:
                if py < self.bot_y - 20:  # Plateforme accessible
                    distance_x = abs(px + pw/2 - self.bot_x)
                    if distance_x < min_distance_above:
                        min_distance_above = distance_x
                        nearest_platform_above = (px, py, pw)
        
        # Se déplacer vers la plateforme cible
        if nearest_platform_above:
            px, py, pw = nearest_platform_above
            target_x = px + pw / 2
            
            # Déplacement horizontal (comme le joueur)
            if self.bot_x < target_x - 15:
                self.bot_x = min(SCREEN_WIDTH - 30, self.bot_x + 5)
            elif self.bot_x > target_x + 15:
                self.bot_x = max(30, self.bot_x - 5)
            
            # Sauter si nécessaire (comme le joueur)
            # Sauter si on est sur une plateforme et qu'il y a une plateforme au-dessus à portée
            if self.bot_on_platform and abs(self.bot_x - target_x) < 60:
                # Vérifier s'il y a une plateforme au-dessus à portée de saut
                for px2, py2, pw2 in self.platforms:
                    if py2 < self.bot_y - 30 and abs((px2 + pw2/2) - self.bot_x) < 80:
                        if self.bot_jump_count < 2:  # Max 2 sauts
                            self.bot_velocity_y = -15  # Même force de saut que le joueur
                            self.bot_jump_count += 1
                            break
            # Sauter aussi si on est en train de tomber et qu'on approche d'une plateforme
            elif self.bot_velocity_y > 0 and abs(self.bot_x - target_x) < 50:
                # Petit saut en l'air si on a encore des sauts disponibles
                if self.bot_jump_count < 2:
                    self.bot_velocity_y = -8  # Petit saut en l'air
                    self.bot_jump_count += 1
        
        # Si le bot est trop bas, essayer de sauter désespérément
        if self.bot_y > SCREEN_HEIGHT - 100 and self.bot_jump_count < 2:
            # Chercher n'importe quelle plateforme au-dessus
            for px, py, pw in self.platforms:
                if py < self.bot_y - 20:
                    if self.bot_jump_count < 2:
                        self.bot_velocity_y = -15
                        self.bot_jump_count += 1
                        break
    
    def _check_platform_collisions(self):
        """Vérifie les collisions avec les plateformes"""
        # Joueur 1
        player1_rect = pygame.Rect(self.player1_x - 15, self.player1_y, 30, 30)
        self.player1_on_platform = False
        for px, py, pw in self.platforms:
            platform_rect = pygame.Rect(px, py, pw, self.platform_height)
            if player1_rect.colliderect(platform_rect):
                # Si le joueur tombe sur la plateforme
                if self.player1_velocity_y >= 0 and self.player1_y < py + self.platform_height:
                    self.player1_y = py - 30
                    self.player1_velocity_y = 0
                    self.player1_on_platform = True
                    # Réinitialiser le compteur de sauts quand on atterrit sur une plateforme
                    self.player1_jump_count = 0
                    break
        
        # Joueur 2 (si PvP)
        if self.match_manager.game_mode == "pvp":
            player2_rect = pygame.Rect(self.player2_x - 15, self.player2_y, 30, 30)
            self.player2_on_platform = False
            for px, py, pw in self.platforms:
                platform_rect = pygame.Rect(px, py, pw, self.platform_height)
                if player2_rect.colliderect(platform_rect):
                    if self.player2_velocity_y >= 0 and self.player2_y < py + self.platform_height:
                        self.player2_y = py - 30
                        self.player2_velocity_y = 0
                        self.player2_on_platform = True
                        # Réinitialiser le compteur de sauts quand on atterrit sur une plateforme
                        self.player2_jump_count = 0
                        break
        
        # Bot (si mode 1v1 ou 2v1)
        if self.match_manager.game_mode != "pvp":
            bot_rect = pygame.Rect(self.bot_x - 15, self.bot_y, 30, 30)
            self.bot_on_platform = False
            for px, py, pw in self.platforms:
                platform_rect = pygame.Rect(px, py, pw, self.platform_height)
                if bot_rect.colliderect(platform_rect):
                    if self.bot_velocity_y >= 0 and self.bot_y < py + self.platform_height:
                        self.bot_y = py - 30
                        self.bot_velocity_y = 0
                        self.bot_on_platform = True
                        # Réinitialiser le compteur de sauts quand on atterrit sur une plateforme
                        self.bot_jump_count = 0
                        break
    
    def get_winner_for_match(self):
        """Retourne le gagnant pour le match_manager"""
        print(f"[DEBUG] Lava Survival - get_winner_for_match: winner={self.winner}, game_over={self.game_over}")
        if self.winner is None:
            print("[DEBUG] Lava Survival - Aucun gagnant déterminé, retourne None")
        return self.winner
    
    def draw(self, screen):
        """Dessine le jeu"""
        if not self.game_active:
            return
        
        # Fond (lave en bas)
        screen.fill((139, 0, 0))  # Rouge foncé (lave)
        # Dégradé vers le haut
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(139 * (1 - ratio) + 25 * ratio)
            g = int(0 * (1 - ratio) + 25 * ratio)
            b = int(0 * (1 - ratio) + 112 * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Titre
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("🔥 LE SOL EST EN LAVE 🔥", True, RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        subtitle = pygame.font.Font(None, 28).render("5 points pour le dernier survivant!", True, YELLOW)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 70))
        
        # Instructions détaillées
        font_small = pygame.font.Font(None, 24)
        font_tiny = pygame.font.Font(None, 20)
        
        # Instructions simplifiées
        if self.match_manager.game_mode == "pvp":
            inst = "J1: Flèches/Space/Manette | J2: J/L/I/Manette | 2 sauts max | Plateformes descendent → Sautez!"
        else:
            inst = "Flèches/Manette: Déplacer | Espace/X: Sauter (2 sauts max) | Plateformes descendent → Sautez!"
        
        inst_text = font_small.render(inst, True, WHITE)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 100))
        
        warning = font_small.render("Touchez le bas = Perdu | Survivez 30s pour gagner!", True, RED)
        screen.blit(warning, (SCREEN_WIDTH // 2 - warning.get_width() // 2, 130))
        
        # Timer de survie
        if not self.game_over:
            timer_text = font_small.render(f"Temps: {int(self.survival_timer)}/{self.survival_time_limit}s", True, GREEN)
            screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 155))
        
        # Dessiner les plateformes
        for px, py, pw in self.platforms:
            if -50 < py < SCREEN_HEIGHT + 50:
                pygame.draw.rect(screen, GREEN, (px, py, pw, self.platform_height))
                pygame.draw.rect(screen, BLACK, (px, py, pw, self.platform_height), 2)
        
        # Dessiner les joueurs
        # Joueur 1 (rouge)
        pygame.draw.circle(screen, RED, (int(self.player1_x), int(self.player1_y)), 15)
        pygame.draw.circle(screen, BLACK, (int(self.player1_x), int(self.player1_y)), 15, 2)
        
        # Joueur 2 (bleu) - seulement en mode PvP
        if self.match_manager.game_mode == "pvp":
            pygame.draw.circle(screen, BLUE, (int(self.player2_x), int(self.player2_y)), 15)
            pygame.draw.circle(screen, BLACK, (int(self.player2_x), int(self.player2_y)), 15, 2)
        
        # Bot (cyan) - pour mode 1v1 et 2v1
        if self.match_manager.game_mode != "pvp":
            pygame.draw.circle(screen, CYAN, (int(self.bot_x), int(self.bot_y)), 15)
            pygame.draw.circle(screen, BLACK, (int(self.bot_x), int(self.bot_y)), 15, 2)
        
        # Message de fin
        if self.game_over:
            font_medium = pygame.font.Font(None, 48)
            if self.winner == 'player1':
                msg = "Joueur 1 survit! +5 points"
                color = RED
            elif self.winner == 'player2':
                msg = "Joueur 2 survit! +5 points"
                color = BLUE
            elif self.winner == 'bot':
                msg = "Bot survit! +5 points"
                color = BLUE
            else:
                msg = "Égalité!"
                color = GRAY
            
            msg_text = font_medium.render(msg, True, color)
            screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 100))
            
            hint = font_small.render("Appuyez sur ESPACE ou X pour continuer", True, WHITE)
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 60))

