"""
Gestion des niveaux - Génération depuis fichier texte
"""
import pygame
from platform import Platform
from enemy import Enemy
from collectible import Collectible
from boss import Boss
from config import *

class Level:
    def __init__(self, level_file=None, level_id=0):
        self.platforms = []
        self.enemies = []
        self.collectibles = []
        self.boss = None  # Boss pour le niveau final
        self.end_x = SCREEN_WIDTH - 100  # Position de fin du niveau
        self.level_id = level_id
        self.level_type = "parkour"  # parkour ou boss
        
        # Vérifier si le fichier existe avant de l'utiliser
        file_exists = False
        if level_file:
            import os
            file_exists = os.path.exists(level_file)
        
        if level_file and file_exists:
            # Charger depuis le fichier si il existe
            self.load_from_file(level_file)
        else:
            # Créer le niveau basé sur level_id
            if level_id == 0:
                self.create_parkour_level_1()
            elif level_id == 1:
                self.create_parkour_level_2()
            elif level_id == 2:
                self.create_boss_level()
            else:
                self.create_default_level()
    
    def create_parkour_level_1(self):
        """Niveau Parkour 1 - Sauts et plateformes (FACILE mais PLUS LONG)"""
        self.level_type = "parkour"
        # Sol étendu (niveau plus long)
        extended_width = SCREEN_WIDTH * 2  # Niveau 2x plus long
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, extended_width),
        ]
        
        # Plateformes de parcours avec sauts (faciles - grandes et proches) - BEAUCOUP PLUS
        platform_positions = [
            # Première section
            (150, 650, 120), (320, 550, 100), (480, 450, 120), (650, 350, 100),
            (800, 550, 120), (970, 450, 100), (1120, 350, 150),
            # Deuxième section (après l'écran initial)
            (1300, 650, 120), (1470, 550, 100), (1630, 450, 120), (1800, 350, 100),
            (1950, 550, 120), (2120, 450, 100), (2270, 350, 150),
            # Troisième section
            (2450, 650, 120), (2620, 550, 100), (2780, 450, 120), (2950, 350, 100),
            (3100, 550, 120), (3270, 450, 100), (3420, 350, 150),
        ]
        
        for x, y, width in platform_positions:
            self.platforms.append(Platform(x, y, width))
        
        # BEAUCOUP PLUS D'ENNEMIS partout (difficulté compétitive) + ENNEMIS VOLANTS
        self.enemies = [
            # Section 1 - Ennemis au sol
            Enemy(180, 650 - ENEMY_HEIGHT, 150, 270),
            Enemy(500, 450 - ENEMY_HEIGHT, 480, 600),
            Enemy(830, 550 - ENEMY_HEIGHT, 800, 920),
            Enemy(1000, 450 - ENEMY_HEIGHT, 970, 1090),
            Enemy(1200, 350 - ENEMY_HEIGHT, 1120, 1270),
            # Section 1 - Ennemis volants en l'air
            Enemy(300, 400, 200, 500, flying=True),
            Enemy(600, 300, 500, 700, flying=True),
            Enemy(900, 500, 800, 1000, flying=True),
            Enemy(1100, 250, 1000, 1200, flying=True),
            # Section 2 - Ennemis au sol
            Enemy(1330, 650 - ENEMY_HEIGHT, 1300, 1420),
            Enemy(1500, 550 - ENEMY_HEIGHT, 1470, 1570),
            Enemy(1660, 450 - ENEMY_HEIGHT, 1630, 1750),
            Enemy(1830, 350 - ENEMY_HEIGHT, 1800, 1900),
            Enemy(1980, 550 - ENEMY_HEIGHT, 1950, 2070),
            Enemy(2150, 450 - ENEMY_HEIGHT, 2120, 2220),
            Enemy(2300, 350 - ENEMY_HEIGHT, 2270, 2420),
            # Section 2 - Ennemis volants
            Enemy(1400, 400, 1300, 1500, flying=True),
            Enemy(1700, 300, 1600, 1800, flying=True),
            Enemy(2000, 500, 1900, 2100, flying=True),
            Enemy(2250, 250, 2150, 2350, flying=True),
            # Section 3 - Ennemis au sol
            Enemy(2480, 650 - ENEMY_HEIGHT, 2450, 2570),
            Enemy(2650, 550 - ENEMY_HEIGHT, 2620, 2720),
            Enemy(2810, 450 - ENEMY_HEIGHT, 2780, 2900),
            Enemy(2980, 350 - ENEMY_HEIGHT, 2950, 3050),
            Enemy(3130, 550 - ENEMY_HEIGHT, 3100, 3220),
            Enemy(3300, 450 - ENEMY_HEIGHT, 3270, 3370),
            Enemy(3450, 350 - ENEMY_HEIGHT, 3420, 3570),
            # Section 3 - Ennemis volants
            Enemy(2550, 400, 2450, 2650, flying=True),
            Enemy(2800, 300, 2700, 2900, flying=True),
            Enemy(3100, 500, 3000, 3200, flying=True),
            Enemy(3350, 250, 3250, 3450, flying=True),
        ]
        
        # Collectibles stratégiquement placés
        self.collectibles = [
            Collectible(210, 650 - ENEMY_HEIGHT - 40),
            Collectible(370, 550 - ENEMY_HEIGHT - 40),
            Collectible(540, 450 - ENEMY_HEIGHT - 40),
            Collectible(700, 350 - ENEMY_HEIGHT - 40),
            Collectible(860, 550 - ENEMY_HEIGHT - 40),
            Collectible(1020, 450 - ENEMY_HEIGHT - 40),
            Collectible(1195, 350 - ENEMY_HEIGHT - 40),
            Collectible(1360, 650 - ENEMY_HEIGHT - 40),
            Collectible(1520, 550 - ENEMY_HEIGHT - 40),
            Collectible(1680, 450 - ENEMY_HEIGHT - 40),
            Collectible(1840, 350 - ENEMY_HEIGHT - 40),
            Collectible(2000, 550 - ENEMY_HEIGHT - 40),
            Collectible(2160, 450 - ENEMY_HEIGHT - 40),
            Collectible(2320, 350 - ENEMY_HEIGHT - 40),
            Collectible(2480, 650 - ENEMY_HEIGHT - 40),
            Collectible(2640, 550 - ENEMY_HEIGHT - 40),
            Collectible(2800, 450 - ENEMY_HEIGHT - 40),
            Collectible(2960, 350 - ENEMY_HEIGHT - 40),
            Collectible(3120, 550 - ENEMY_HEIGHT - 40),
            Collectible(3280, 450 - ENEMY_HEIGHT - 40),
            Collectible(3440, 350 - ENEMY_HEIGHT - 40),
        ]
        
        self.end_x = extended_width - 50
    
    def create_boss_level(self):
        """Niveau Boss Final - Combat contre le grand robot"""
        self.level_type = "boss"
        # Sol plat pour la course contre le boss
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH),
        ]
        
        # Quelques plateformes pour le combat
        self.platforms.extend([
            Platform(300, SCREEN_HEIGHT - 150, 80),
            Platform(600, SCREEN_HEIGHT - 200, 80),
            Platform(900, SCREEN_HEIGHT - 150, 80),
        ])
        
        # Le grand boss robot (position de départ à droite)
        self.boss = Boss(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150)
        
        # Pas d'ennemis normaux, juste le boss
        self.enemies = []
        
        # Quelques collectibles pour le score
        self.collectibles = [
            Collectible(400, SCREEN_HEIGHT - 200),
            Collectible(700, SCREEN_HEIGHT - 250),
            Collectible(1000, SCREEN_HEIGHT - 200),
        ]
        
        self.end_x = SCREEN_WIDTH - 50
    
    def create_parkour_level_2(self):
        """Niveau Parkour 2 - Défi de précision (DIFFICULTÉ AUGMENTÉE et PLUS LONG)"""
        self.level_type = "parkour"
        # Sol étendu (niveau plus long)
        extended_width = SCREEN_WIDTH * 2.5  # Niveau 2.5x plus long
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, extended_width),
        ]
        
        # Plateformes plus petites et espacées (défi de précision) - BEAUCOUP PLUS
        platform_positions = [
            # Section 1
            (100, 700, 50), (220, 600, 45), (350, 500, 50), (480, 400, 45),
            (610, 500, 50), (740, 400, 45), (870, 300, 50), (1000, 400, 45), (1130, 500, 50),
            # Section 2
            (1300, 700, 45), (1420, 600, 50), (1550, 500, 45), (1680, 400, 50),
            (1810, 500, 45), (1940, 400, 50), (2070, 300, 45), (2200, 400, 50), (2330, 500, 45),
            # Section 3
            (2460, 700, 50), (2590, 600, 45), (2720, 500, 50), (2850, 400, 45),
            (2980, 500, 50), (3110, 400, 45), (3240, 300, 50), (3370, 400, 45), (3500, 500, 50),
        ]
        
        for x, y, width in platform_positions:
            self.platforms.append(Platform(x, y, width))
        
        # BEAUCOUP PLUS D'ENNEMIS partout (difficulté compétitive maximale) + ENNEMIS VOLANTS
        self.enemies = [
            # Section 1 - Ennemis au sol
            Enemy(120, 700 - ENEMY_HEIGHT, 100, 150),
            Enemy(240, 600 - ENEMY_HEIGHT, 220, 270),
            Enemy(370, 500 - ENEMY_HEIGHT, 350, 400),
            Enemy(500, 400 - ENEMY_HEIGHT, 480, 530),
            Enemy(630, 500 - ENEMY_HEIGHT, 610, 660),
            Enemy(760, 400 - ENEMY_HEIGHT, 740, 790),
            Enemy(890, 300 - ENEMY_HEIGHT, 870, 920),
            Enemy(1020, 400 - ENEMY_HEIGHT, 1000, 1050),
            Enemy(1160, 500 - ENEMY_HEIGHT, 1130, 1180),
            # Section 1 - Ennemis volants
            Enemy(200, 450, 100, 300, flying=True),
            Enemy(450, 350, 350, 550, flying=True),
            Enemy(700, 550, 600, 800, flying=True),
            Enemy(950, 250, 850, 1050, flying=True),
            # Section 2 - Ennemis au sol
            Enemy(1330, 700 - ENEMY_HEIGHT, 1300, 1365),
            Enemy(1450, 600 - ENEMY_HEIGHT, 1420, 1470),
            Enemy(1580, 500 - ENEMY_HEIGHT, 1550, 1600),
            Enemy(1710, 400 - ENEMY_HEIGHT, 1680, 1730),
            Enemy(1840, 500 - ENEMY_HEIGHT, 1810, 1855),
            Enemy(1970, 400 - ENEMY_HEIGHT, 1940, 1990),
            Enemy(2100, 300 - ENEMY_HEIGHT, 2070, 2115),
            Enemy(2230, 400 - ENEMY_HEIGHT, 2200, 2250),
            Enemy(2360, 500 - ENEMY_HEIGHT, 2330, 2375),
            # Section 2 - Ennemis volants
            Enemy(1400, 450, 1300, 1500, flying=True),
            Enemy(1650, 350, 1550, 1750, flying=True),
            Enemy(1900, 550, 1800, 2000, flying=True),
            Enemy(2150, 250, 2050, 2250, flying=True),
            # Section 3 - Ennemis au sol
            Enemy(2490, 700 - ENEMY_HEIGHT, 2460, 2510),
            Enemy(2620, 600 - ENEMY_HEIGHT, 2590, 2635),
            Enemy(2750, 500 - ENEMY_HEIGHT, 2720, 2770),
            Enemy(2880, 400 - ENEMY_HEIGHT, 2850, 2895),
            Enemy(3010, 500 - ENEMY_HEIGHT, 2980, 3030),
            Enemy(3140, 400 - ENEMY_HEIGHT, 3110, 3155),
            Enemy(3270, 300 - ENEMY_HEIGHT, 3240, 3290),
            Enemy(3400, 400 - ENEMY_HEIGHT, 3370, 3415),
            Enemy(3530, 500 - ENEMY_HEIGHT, 3500, 3550),
            # Section 3 - Ennemis volants
            Enemy(2600, 450, 2500, 2700, flying=True),
            Enemy(2850, 350, 2750, 2950, flying=True),
            Enemy(3100, 550, 3000, 3200, flying=True),
            Enemy(3350, 250, 3250, 3450, flying=True),
        ]
        
        # Collectibles sur chaque plateforme
        self.collectibles = [
            Collectible(125, 700 - ENEMY_HEIGHT - 40),
            Collectible(242, 600 - ENEMY_HEIGHT - 40),
            Collectible(375, 500 - ENEMY_HEIGHT - 40),
            Collectible(502, 400 - ENEMY_HEIGHT - 40),
            Collectible(635, 500 - ENEMY_HEIGHT - 40),
            Collectible(762, 400 - ENEMY_HEIGHT - 40),
            Collectible(895, 300 - ENEMY_HEIGHT - 40),
            Collectible(1025, 400 - ENEMY_HEIGHT - 40),
            Collectible(1155, 500 - ENEMY_HEIGHT - 40),
            Collectible(1325, 700 - ENEMY_HEIGHT - 40),
            Collectible(1445, 600 - ENEMY_HEIGHT - 40),
            Collectible(1575, 500 - ENEMY_HEIGHT - 40),
            Collectible(1705, 400 - ENEMY_HEIGHT - 40),
            Collectible(1835, 500 - ENEMY_HEIGHT - 40),
            Collectible(1965, 400 - ENEMY_HEIGHT - 40),
            Collectible(2095, 300 - ENEMY_HEIGHT - 40),
            Collectible(2225, 400 - ENEMY_HEIGHT - 40),
            Collectible(2355, 500 - ENEMY_HEIGHT - 40),
            Collectible(2485, 700 - ENEMY_HEIGHT - 40),
            Collectible(2615, 600 - ENEMY_HEIGHT - 40),
            Collectible(2745, 500 - ENEMY_HEIGHT - 40),
            Collectible(2875, 400 - ENEMY_HEIGHT - 40),
            Collectible(3005, 500 - ENEMY_HEIGHT - 40),
            Collectible(3135, 400 - ENEMY_HEIGHT - 40),
            Collectible(3265, 300 - ENEMY_HEIGHT - 40),
            Collectible(3395, 400 - ENEMY_HEIGHT - 40),
            Collectible(3525, 500 - ENEMY_HEIGHT - 40),
        ]
        
        self.end_x = extended_width - 50
    
    def create_default_level(self):
        """Crée un niveau par défaut si aucun fichier n'est fourni"""
        self.create_parkour_level_1()
    
    def load_from_file(self, filename):
        """Charge un niveau depuis un fichier texte"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            # Format: chaque ligne représente une ligne du niveau
            # '1' = plateforme, '0' = vide, 'E' = ennemi, 'C' = collectible, 'P' = position joueur
            cell_size = 40  # Taille de chaque cellule
            
            for y, line in enumerate(lines):
                for x, char in enumerate(line.strip()):
                    px = x * cell_size
                    py = y * cell_size
                    
                    if char == '1':  # Plateforme
                        # Vérifier si une plateforme continue existe déjà
                        found = False
                        for platform in self.platforms:
                            if platform.rect.y == py and platform.rect.right == px:
                                platform.rect.width += cell_size
                                found = True
                                break
                        if not found:
                            self.platforms.append(Platform(px, py, cell_size))
                    
                    elif char == 'E':  # Ennemi
                        # Trouver la plateforme sous l'ennemi
                        platform_left = px
                        platform_right = px + cell_size
                        for platform in self.platforms:
                            if platform.rect.y == py + cell_size:
                                platform_left = platform.rect.left
                                platform_right = platform.rect.right
                                break
                        self.enemies.append(Enemy(px, py, platform_left, platform_right))
                    
                    elif char == 'C':  # Collectible
                        self.collectibles.append(Collectible(px, py))
                    
                    elif char == 'F':  # Fin du niveau
                        self.end_x = px
        
        except FileNotFoundError:
            print(f"Fichier {filename} non trouvé, utilisation du niveau par défaut")
            self.create_default_level()
    
    def update(self, player):
        """Met à jour tous les éléments du niveau"""
        # Mettre à jour les ennemis
        for enemy in self.enemies:
            enemy.update(self.platforms, player)
        
        # Mettre à jour le boss si présent
        if self.boss:
            self.boss.update(self.platforms, player)
        
        # Mettre à jour les collectibles
        for collectible in self.collectibles:
            collectible.update()
    
    def draw(self, screen, camera_x=0):
        """Dessine tous les éléments du niveau avec décalage de caméra"""
        # Dessiner les plateformes avec décalage de caméra
        for platform in self.platforms:
            # Vérifier si la plateforme est visible à l'écran
            if platform.rect.right - camera_x > 0 and platform.rect.left - camera_x < SCREEN_WIDTH:
                # Sauvegarder la position originale
                old_x = platform.rect.x
                platform.rect.x -= camera_x
                platform.draw(screen)
                platform.rect.x = old_x  # Restaurer
        
        # Dessiner les collectibles avec décalage de caméra
        for collectible in self.collectibles:
            if collectible.rect.right - camera_x > 0 and collectible.rect.left - camera_x < SCREEN_WIDTH:
                old_x = collectible.rect.x
                collectible.rect.x -= camera_x
                collectible.draw(screen)
                collectible.rect.x = old_x
        
        # Dessiner les ennemis avec décalage de caméra
        for enemy in self.enemies:
            if enemy.rect.right - camera_x > 0 and enemy.rect.left - camera_x < SCREEN_WIDTH:
                old_x = enemy.rect.x
                enemy.rect.x -= camera_x
                enemy.draw(screen)
                enemy.rect.x = old_x
        
        # Dessiner le boss si présent avec décalage de caméra
        if self.boss:
            if self.boss.rect.right - camera_x > 0 and self.boss.rect.left - camera_x < SCREEN_WIDTH:
                old_x = self.boss.rect.x
                self.boss.rect.x -= camera_x
                self.boss.draw(screen)
                self.boss.rect.x = old_x
        
        # Dessiner la zone de fin (drapeau style pixel art) avec décalage de caméra
        flag_pole_x = self.end_x - camera_x
        flag_pole_y = SCREEN_HEIGHT - 150
        flag_pole_height = 100
        
        # Mât du drapeau
        pygame.draw.line(screen, (139, 69, 19),  # Marron
                         (flag_pole_x, flag_pole_y),
                         (flag_pole_x, flag_pole_y + flag_pole_height), 5)
        
        # Drapeau (carré avec damier)
        flag_width = 40
        flag_height = 30
        flag_rect = pygame.Rect(flag_pole_x + 5, flag_pole_y, flag_width, flag_height)
        
        # Fond du drapeau (jaune et rouge en damier)
        for i in range(2):
            for j in range(2):
                cell_rect = pygame.Rect(
                    flag_rect.x + i * flag_width // 2,
                    flag_rect.y + j * flag_height // 2,
                    flag_width // 2,
                    flag_height // 2
                )
                if (i + j) % 2 == 0:
                    pygame.draw.rect(screen, YELLOW, cell_rect)
                else:
                    pygame.draw.rect(screen, RED, cell_rect)
                pygame.draw.rect(screen, BLACK, cell_rect, 1)
        
        # Texte "FIN" ou "GOAL"
        font = pygame.font.Font(None, 24)
        text = font.render("GOAL", True, BLACK)
        text_rect = text.get_rect(center=(flag_rect.centerx, flag_rect.centery))
        screen.blit(text, text_rect)
    
    def check_level_complete(self, player):
        """Vérifie si le joueur a atteint la fin du niveau"""
        if self.level_type == "boss":
            # En mode boss, le niveau est terminé si le boss est vaincu
            return self.boss is None or not self.boss.alive
        else:
            # En mode parcours, le niveau est terminé quand on atteint la fin
            return player.rect.right >= self.end_x

