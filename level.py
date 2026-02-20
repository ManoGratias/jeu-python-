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
        self.checkpoints = []  # Liste de (x, y) pour les points de respawn
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
                self.create_parkour_level_3()
            elif level_id == 3:
                self.create_parkour_level_4()
            elif level_id == 4:
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
        
        # NIVEAU 1 TRÈS FACILE - Peu d'ennemis pour bien débuter
        self.enemies = [
            # Section 1 - Quelques ennemis au sol
            Enemy(500, 450 - ENEMY_HEIGHT, 480, 600),
            Enemy(1000, 450 - ENEMY_HEIGHT, 970, 1090),
            # Section 1 - Un seul ennemi volant
            Enemy(600, 300, 500, 700, flying=True),
            # Section 2 - Quelques ennemis
            Enemy(1660, 450 - ENEMY_HEIGHT, 1630, 1750),
            Enemy(2150, 450 - ENEMY_HEIGHT, 2120, 2220),
            Enemy(1700, 300, 1600, 1800, flying=True),
            # Section 3 - Quelques ennemis
            Enemy(2810, 450 - ENEMY_HEIGHT, 2780, 2900),
            Enemy(3300, 450 - ENEMY_HEIGHT, 3270, 3370),
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
        
        # Checkpoints - points de respawn (environ tous les 1/3 du niveau)
        self.checkpoints = [
            (50, 100),      # Départ
            (800, 350),     # Après 1ère section
            (1800, 350),    # Milieu
            (2800, 350),    # Avant la fin
        ]
        self.end_x = extended_width - 50
    
    def create_boss_level(self):
        """Niveau Boss Final - Le boss reste au fond et tire des ennemis au sol et en l'air"""
        self.level_type = "boss"
        extended_width = SCREEN_WIDTH * 2  # Niveau plus long
        # IMPORTANT: Ne pas initialiser boss_start_time ici
        # Le timer sera initialisé seulement quand l'animation "Manche X" est terminée
        self.boss_start_time = None  # Sera initialisé quand le jeu commence vraiment
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, extended_width),
        ]
        # Plateformes pour le parcours (obstacles) + plateformes en hauteur pour tuer les ennemis volants
        platform_positions = [
            # Plateformes basses (parcours principal)
            (200, SCREEN_HEIGHT - 180, 70), (450, SCREEN_HEIGHT - 220, 60),
            (700, SCREEN_HEIGHT - 160, 80), (950, SCREEN_HEIGHT - 200, 65),
            (1200, SCREEN_HEIGHT - 180, 70), (1500, SCREEN_HEIGHT - 240, 55),
            (1800, SCREEN_HEIGHT - 170, 75), (2100, SCREEN_HEIGHT - 210, 60),
            (2400, SCREEN_HEIGHT - 190, 70),
            # Plateformes moyennes (pour sauter vers les ennemis volants)
            (300, SCREEN_HEIGHT - 350, 60), (600, SCREEN_HEIGHT - 380, 55),
            (900, SCREEN_HEIGHT - 320, 65), (1100, SCREEN_HEIGHT - 360, 60),
            (1400, SCREEN_HEIGHT - 340, 70), (1700, SCREEN_HEIGHT - 380, 55),
            (2000, SCREEN_HEIGHT - 350, 65), (2300, SCREEN_HEIGHT - 370, 60),
            # Plateformes hautes (pour atteindre les ennemis volants en haut)
            (400, SCREEN_HEIGHT - 500, 50), (750, SCREEN_HEIGHT - 520, 55),
            (1050, SCREEN_HEIGHT - 480, 60), (1350, SCREEN_HEIGHT - 510, 50),
            (1650, SCREEN_HEIGHT - 490, 55), (1950, SCREEN_HEIGHT - 520, 60),
            (2250, SCREEN_HEIGHT - 500, 55),
            # Plateformes très hautes (pour les ennemis volants les plus hauts)
            (500, SCREEN_HEIGHT - 650, 45), (850, SCREEN_HEIGHT - 680, 50),
            (1250, SCREEN_HEIGHT - 640, 55), (1600, SCREEN_HEIGHT - 670, 50),
            (2000, SCREEN_HEIGHT - 650, 45), (2350, SCREEN_HEIGHT - 680, 50),
        ]
        for x, y, w in platform_positions:
            self.platforms.append(Platform(x, y, w))
        
        # Boss fixe en haut à droite - 3 phases : sol (10), air (10), les deux
        self.boss = Boss(extended_width - 120, 60)
        
        # Pas d'ennemis initiaux - le boss les lance selon les phases
        self.enemies = []
        
        # Pas d'étoiles jaunes en manche 5 - étoiles rouges (phase 1 et 3) et bleues (phase 2 et 3)
        # Les étoiles seront ajoutées dynamiquement selon la phase du boss
        self.collectibles = []
        self.red_stars_added = False  # Étoiles rouges ajoutées en phase 1
        self.blue_stars_added = False  # Étoiles bleues ajoutées en phase 2
        self.bounds_x = (0, extended_width)  # Limites pour ne pas tomber sur les côtés
        self.checkpoints = []  # Pas de checkpoints en manche 5
        self.end_x = extended_width - 50
    
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
        
        # NIVEAU 2 MOINS FACILE - Plus d'ennemis que niveau 1, difficulté progressive
        self.enemies = [
            # Section 1 - Ennemis au sol
            Enemy(240, 600 - ENEMY_HEIGHT, 220, 270),
            Enemy(500, 400 - ENEMY_HEIGHT, 480, 530),
            Enemy(760, 400 - ENEMY_HEIGHT, 740, 790),
            Enemy(890, 300 - ENEMY_HEIGHT, 870, 920),
            Enemy(1020, 400 - ENEMY_HEIGHT, 1000, 1050),
            # Section 1 - Ennemis volants
            Enemy(450, 350, 350, 550, flying=True),
            Enemy(700, 550, 600, 800, flying=True),
            Enemy(950, 250, 850, 1050, flying=True),
            # Section 2 - Ennemis au sol
            Enemy(1450, 600 - ENEMY_HEIGHT, 1420, 1470),
            Enemy(1710, 400 - ENEMY_HEIGHT, 1680, 1730),
            Enemy(1970, 400 - ENEMY_HEIGHT, 1940, 1990),
            Enemy(2100, 300 - ENEMY_HEIGHT, 2070, 2115),
            Enemy(2230, 400 - ENEMY_HEIGHT, 2200, 2250),
            # Section 2 - Ennemis volants
            Enemy(1650, 350, 1550, 1750, flying=True),
            Enemy(1900, 550, 1800, 2000, flying=True),
            # Section 3 - Ennemis au sol
            Enemy(2620, 600 - ENEMY_HEIGHT, 2590, 2635),
            Enemy(2880, 400 - ENEMY_HEIGHT, 2850, 2895),
            Enemy(3140, 400 - ENEMY_HEIGHT, 3110, 3155),
            Enemy(3270, 300 - ENEMY_HEIGHT, 3240, 3290),
            Enemy(3400, 400 - ENEMY_HEIGHT, 3370, 3415),
            # Section 3 - Ennemis volants
            Enemy(2850, 350, 2750, 2950, flying=True),
            Enemy(3100, 550, 3000, 3200, flying=True),
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
        
        # Checkpoints niveau 2
        self.checkpoints = [
            (50, 100), (600, 500), (1500, 500), (2500, 500), (3300, 300)
        ]
        self.end_x = extended_width - 50
    
    def create_parkour_level_3(self):
        """Niveau Parkour 3 - DIFFICILE (plus dur que niveau 2)"""
        self.level_type = "parkour"
        extended_width = SCREEN_WIDTH * 2.5
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, extended_width),
        ]
        platform_positions = [
            (80, 710, 45), (200, 610, 40), (330, 510, 45), (460, 410, 40),
            (590, 510, 45), (720, 410, 40), (850, 310, 45), (980, 410, 40), (1110, 510, 45),
            (1280, 710, 40), (1400, 610, 45), (1530, 510, 40), (1660, 410, 45),
            (1790, 510, 40), (1920, 410, 40), (2050, 310, 45), (2180, 410, 40), (2310, 510, 45),
            (2440, 710, 45), (2570, 610, 40), (2700, 510, 45), (2830, 410, 40),
            (2960, 510, 45), (3090, 410, 40), (3220, 310, 45), (3350, 410, 40), (3480, 510, 45),
        ]
        for x, y, width in platform_positions:
            self.platforms.append(Platform(x, y, width))
        
        # NIVEAU 3 DIFFICILE - Beaucoup plus d'ennemis que niveau 2
        self.enemies = [
            Enemy(120, 610 - ENEMY_HEIGHT, 80, 160),
            Enemy(260, 510 - ENEMY_HEIGHT, 200, 320),
            Enemy(400, 410 - ENEMY_HEIGHT, 330, 470),
            Enemy(540, 510 - ENEMY_HEIGHT, 460, 620),
            Enemy(680, 410 - ENEMY_HEIGHT, 590, 770),
            Enemy(820, 310 - ENEMY_HEIGHT, 720, 920),
            Enemy(960, 410 - ENEMY_HEIGHT, 850, 1070),
            Enemy(1100, 510 - ENEMY_HEIGHT, 980, 1220),
            Enemy(250, 350, 150, 350, flying=True),
            Enemy(500, 250, 400, 600, flying=True),
            Enemy(750, 450, 650, 850, flying=True),
            Enemy(1000, 200, 900, 1100, flying=True),
            Enemy(1350, 610 - ENEMY_HEIGHT, 1280, 1420),
            Enemy(1490, 510 - ENEMY_HEIGHT, 1400, 1580),
            Enemy(1630, 410 - ENEMY_HEIGHT, 1530, 1730),
            Enemy(1770, 510 - ENEMY_HEIGHT, 1660, 1880),
            Enemy(1910, 410 - ENEMY_HEIGHT, 1790, 2030),
            Enemy(2050, 310 - ENEMY_HEIGHT, 1920, 2180),
            Enemy(2190, 410 - ENEMY_HEIGHT, 2050, 2330),
            Enemy(1400, 350, 1280, 1520, flying=True),
            Enemy(1700, 250, 1600, 1800, flying=True),
            Enemy(2000, 450, 1900, 2100, flying=True),
            Enemy(2500, 610 - ENEMY_HEIGHT, 2440, 2560),
            Enemy(2640, 510 - ENEMY_HEIGHT, 2570, 2710),
            Enemy(2780, 410 - ENEMY_HEIGHT, 2700, 2860),
            Enemy(2920, 510 - ENEMY_HEIGHT, 2830, 3010),
            Enemy(3060, 410 - ENEMY_HEIGHT, 2960, 3160),
            Enemy(3200, 310 - ENEMY_HEIGHT, 3090, 3310),
            Enemy(2600, 350, 2500, 2700, flying=True),
            Enemy(2900, 250, 2800, 3000, flying=True),
            Enemy(3200, 450, 3100, 3300, flying=True),
        ]
        
        self.collectibles = [
            Collectible(105, 710 - ENEMY_HEIGHT - 40), Collectible(225, 610 - ENEMY_HEIGHT - 40),
            Collectible(355, 510 - ENEMY_HEIGHT - 40), Collectible(485, 410 - ENEMY_HEIGHT - 40),
            Collectible(615, 510 - ENEMY_HEIGHT - 40), Collectible(745, 410 - ENEMY_HEIGHT - 40),
            Collectible(875, 310 - ENEMY_HEIGHT - 40), Collectible(1005, 410 - ENEMY_HEIGHT - 40),
            Collectible(1135, 510 - ENEMY_HEIGHT - 40), Collectible(1305, 710 - ENEMY_HEIGHT - 40),
            Collectible(1425, 610 - ENEMY_HEIGHT - 40), Collectible(1555, 510 - ENEMY_HEIGHT - 40),
            Collectible(1685, 410 - ENEMY_HEIGHT - 40), Collectible(1815, 510 - ENEMY_HEIGHT - 40),
            Collectible(1945, 410 - ENEMY_HEIGHT - 40), Collectible(2075, 310 - ENEMY_HEIGHT - 40),
            Collectible(2205, 410 - ENEMY_HEIGHT - 40), Collectible(2335, 510 - ENEMY_HEIGHT - 40),
            Collectible(2465, 710 - ENEMY_HEIGHT - 40), Collectible(2595, 610 - ENEMY_HEIGHT - 40),
            Collectible(2725, 510 - ENEMY_HEIGHT - 40), Collectible(2855, 410 - ENEMY_HEIGHT - 40),
            Collectible(2985, 510 - ENEMY_HEIGHT - 40), Collectible(3115, 410 - ENEMY_HEIGHT - 40),
            Collectible(3245, 310 - ENEMY_HEIGHT - 40), Collectible(3375, 410 - ENEMY_HEIGHT - 40),
        ]
        self.checkpoints = [(50, 100), (800, 410), (1700, 410), (2600, 510), (3400, 410)]
        self.end_x = extended_width - 50
    
    def create_parkour_level_4(self):
        """Niveau Parkour 4 - TRÈS DIFFICILE (plus dur que niveau 3)"""
        self.level_type = "parkour"
        extended_width = SCREEN_WIDTH * 2.5
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, extended_width),
        ]
        platform_positions = [
            (70, 720, 40), (190, 620, 38), (310, 520, 40), (430, 420, 38),
            (550, 520, 40), (670, 420, 38), (790, 320, 40), (910, 420, 38), (1030, 520, 40), (1150, 620, 38),
            (1270, 720, 38), (1390, 620, 40), (1510, 520, 38), (1630, 420, 40),
            (1750, 520, 38), (1870, 420, 40), (1990, 320, 38), (2110, 420, 40), (2230, 520, 38), (2350, 620, 40),
            (2470, 720, 40), (2590, 620, 38), (2710, 520, 40), (2830, 420, 38),
            (2950, 520, 40), (3070, 420, 38), (3190, 320, 40), (3310, 420, 38), (3430, 520, 40), (3550, 620, 40),
        ]
        for x, y, width in platform_positions:
            self.platforms.append(Platform(x, y, width))
        
        # NIVEAU 4 TRÈS DIFFICILE - Maximum d'ennemis, plateformes petites
        self.enemies = [
            Enemy(100, 620 - ENEMY_HEIGHT, 70, 130),
            Enemy(230, 520 - ENEMY_HEIGHT, 190, 270),
            Enemy(360, 420 - ENEMY_HEIGHT, 310, 410),
            Enemy(490, 520 - ENEMY_HEIGHT, 430, 550),
            Enemy(620, 420 - ENEMY_HEIGHT, 550, 690),
            Enemy(750, 320 - ENEMY_HEIGHT, 670, 830),
            Enemy(880, 420 - ENEMY_HEIGHT, 790, 970),
            Enemy(1010, 520 - ENEMY_HEIGHT, 910, 1110),
            Enemy(1140, 620 - ENEMY_HEIGHT, 1030, 1250),
            Enemy(200, 300, 100, 300, flying=True),
            Enemy(450, 200, 350, 550, flying=True),
            Enemy(700, 400, 600, 800, flying=True),
            Enemy(950, 150, 850, 1050, flying=True),
            Enemy(1200, 500, 1100, 1300, flying=True),
            Enemy(1320, 620 - ENEMY_HEIGHT, 1270, 1370),
            Enemy(1440, 520 - ENEMY_HEIGHT, 1390, 1490),
            Enemy(1560, 420 - ENEMY_HEIGHT, 1510, 1610),
            Enemy(1680, 520 - ENEMY_HEIGHT, 1630, 1730),
            Enemy(1800, 420 - ENEMY_HEIGHT, 1750, 1850),
            Enemy(1920, 320 - ENEMY_HEIGHT, 1870, 1970),
            Enemy(2040, 420 - ENEMY_HEIGHT, 1990, 2090),
            Enemy(2160, 520 - ENEMY_HEIGHT, 2110, 2210),
            Enemy(2280, 620 - ENEMY_HEIGHT, 2230, 2330),
            Enemy(1380, 320, 1270, 1490, flying=True),
            Enemy(1680, 220, 1570, 1790, flying=True),
            Enemy(1980, 420, 1870, 2090, flying=True),
            Enemy(2280, 180, 2170, 2390, flying=True),
            Enemy(2520, 620 - ENEMY_HEIGHT, 2470, 2570),
            Enemy(2640, 520 - ENEMY_HEIGHT, 2590, 2690),
            Enemy(2760, 420 - ENEMY_HEIGHT, 2710, 2810),
            Enemy(2880, 520 - ENEMY_HEIGHT, 2830, 2930),
            Enemy(3000, 420 - ENEMY_HEIGHT, 2950, 3050),
            Enemy(3120, 320 - ENEMY_HEIGHT, 3070, 3170),
            Enemy(3240, 420 - ENEMY_HEIGHT, 3190, 3290),
            Enemy(3360, 520 - ENEMY_HEIGHT, 3310, 3410),
            Enemy(2550, 300, 2470, 2630, flying=True),
            Enemy(2850, 200, 2750, 2950, flying=True),
            Enemy(3150, 400, 3050, 3250, flying=True),
            Enemy(3450, 250, 3350, 3550, flying=True),
        ]
        
        self.collectibles = [
            Collectible(95, 720 - ENEMY_HEIGHT - 40), Collectible(215, 620 - ENEMY_HEIGHT - 40),
            Collectible(335, 520 - ENEMY_HEIGHT - 40), Collectible(455, 420 - ENEMY_HEIGHT - 40),
            Collectible(575, 520 - ENEMY_HEIGHT - 40), Collectible(695, 420 - ENEMY_HEIGHT - 40),
            Collectible(815, 320 - ENEMY_HEIGHT - 40), Collectible(935, 420 - ENEMY_HEIGHT - 40),
            Collectible(1055, 520 - ENEMY_HEIGHT - 40), Collectible(1175, 620 - ENEMY_HEIGHT - 40),
            Collectible(1295, 720 - ENEMY_HEIGHT - 40), Collectible(1415, 620 - ENEMY_HEIGHT - 40),
            Collectible(1535, 520 - ENEMY_HEIGHT - 40), Collectible(1655, 420 - ENEMY_HEIGHT - 40),
            Collectible(1775, 520 - ENEMY_HEIGHT - 40), Collectible(1895, 420 - ENEMY_HEIGHT - 40),
            Collectible(2015, 320 - ENEMY_HEIGHT - 40), Collectible(2135, 420 - ENEMY_HEIGHT - 40),
            Collectible(2255, 520 - ENEMY_HEIGHT - 40), Collectible(2375, 620 - ENEMY_HEIGHT - 40),
            Collectible(2495, 720 - ENEMY_HEIGHT - 40), Collectible(2615, 620 - ENEMY_HEIGHT - 40),
            Collectible(2735, 520 - ENEMY_HEIGHT - 40), Collectible(2855, 420 - ENEMY_HEIGHT - 40),
            Collectible(2975, 520 - ENEMY_HEIGHT - 40), Collectible(3095, 420 - ENEMY_HEIGHT - 40),
            Collectible(3215, 320 - ENEMY_HEIGHT - 40), Collectible(3335, 420 - ENEMY_HEIGHT - 40),
            Collectible(3455, 520 - ENEMY_HEIGHT - 40),
        ]
        self.checkpoints = [(50, 100), (900, 420), (1800, 420), (2700, 520), (3500, 420)]
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
            self.boss.update(self.platforms, player, self)
            
            # Ajouter les étoiles selon les phases du boss
            if self.level_type == "boss" and self.boss:
                current_phase = self.boss.phase
                
                # Phase 1 : seulement étoiles rouges
                if current_phase == 1:
                    if not self.red_stars_added:
                        self.red_stars_added = True
                        self.blue_stars_added = False  # Réinitialiser pour la phase suivante
                        # Retirer toutes les étoiles bleues si présentes
                        self.collectibles = [c for c in self.collectibles if c.collect_type != "kill_flying"]
                        # Ajouter les étoiles rouges
                        red_positions = [
                            # Sur plateformes basses
                            (250, SCREEN_HEIGHT - 230), (350, SCREEN_HEIGHT - 230), (500, SCREEN_HEIGHT - 270),
                            (600, SCREEN_HEIGHT - 270), (850, SCREEN_HEIGHT - 210), (950, SCREEN_HEIGHT - 210),
                            (1150, SCREEN_HEIGHT - 230), (1250, SCREEN_HEIGHT - 230), (1550, SCREEN_HEIGHT - 290),
                            (1650, SCREEN_HEIGHT - 290), (1950, SCREEN_HEIGHT - 260), (2050, SCREEN_HEIGHT - 260),
                            (2350, SCREEN_HEIGHT - 240),
                            # Sur plateformes moyennes
                            (300, SCREEN_HEIGHT - 380), (600, SCREEN_HEIGHT - 410), (900, SCREEN_HEIGHT - 350),
                            (1100, SCREEN_HEIGHT - 390), (1400, SCREEN_HEIGHT - 370), (1700, SCREEN_HEIGHT - 410),
                            (2000, SCREEN_HEIGHT - 380), (2300, SCREEN_HEIGHT - 400),
                        ]
                        for px, py in red_positions:
                            self.collectibles.append(Collectible(px, py, collect_type="kill_ground"))
                
                # Phase 2 : seulement étoiles bleues
                elif current_phase == 2:
                    if not self.blue_stars_added:
                        self.blue_stars_added = True
                        self.red_stars_added = False  # Réinitialiser pour la phase suivante
                        # Retirer toutes les étoiles rouges de la phase 1
                        self.collectibles = [c for c in self.collectibles if c.collect_type != "kill_ground"]
                        # Ajouter les étoiles bleues
                        blue_positions = [
                            # Sur plateformes hautes
                            (400, SCREEN_HEIGHT - 530), (500, SCREEN_HEIGHT - 530), (750, SCREEN_HEIGHT - 550),
                            (850, SCREEN_HEIGHT - 550), (1050, SCREEN_HEIGHT - 510), (1150, SCREEN_HEIGHT - 510),
                            (1350, SCREEN_HEIGHT - 540), (1450, SCREEN_HEIGHT - 540), (1650, SCREEN_HEIGHT - 520),
                            (1750, SCREEN_HEIGHT - 520), (1950, SCREEN_HEIGHT - 550), (2050, SCREEN_HEIGHT - 550),
                            (2250, SCREEN_HEIGHT - 530), (2350, SCREEN_HEIGHT - 530),
                            # Sur plateformes très hautes
                            (500, SCREEN_HEIGHT - 680), (600, SCREEN_HEIGHT - 680), (850, SCREEN_HEIGHT - 710),
                            (950, SCREEN_HEIGHT - 710), (1250, SCREEN_HEIGHT - 670), (1350, SCREEN_HEIGHT - 670),
                            (1600, SCREEN_HEIGHT - 700), (1700, SCREEN_HEIGHT - 700), (2000, SCREEN_HEIGHT - 680),
                            (2100, SCREEN_HEIGHT - 680), (2350, SCREEN_HEIGHT - 710), (2450, SCREEN_HEIGHT - 710),
                            # Sur plateformes moyennes aussi
                            (350, SCREEN_HEIGHT - 400), (650, SCREEN_HEIGHT - 420), (950, SCREEN_HEIGHT - 360),
                            (1150, SCREEN_HEIGHT - 400), (1450, SCREEN_HEIGHT - 380), (1750, SCREEN_HEIGHT - 420),
                            (2050, SCREEN_HEIGHT - 390),
                        ]
                        for px, py in blue_positions:
                            self.collectibles.append(Collectible(px, py, collect_type="kill_flying"))
                
                # Phase 3 : les deux types d'étoiles (rouges + bleues)
                elif current_phase == 3:
                    # Réinitialiser les flags pour réajouter les étoiles
                    if not self.red_stars_added or not self.blue_stars_added:
                        # Retirer toutes les étoiles existantes
                        self.collectibles = [c for c in self.collectibles if c.collect_type not in ["kill_ground", "kill_flying"]]
                        self.red_stars_added = False
                        self.blue_stars_added = False
                    
                    if not self.red_stars_added:
                        self.red_stars_added = True
                        red_positions = [
                            # Sur plateformes basses
                            (250, SCREEN_HEIGHT - 230), (350, SCREEN_HEIGHT - 230), (500, SCREEN_HEIGHT - 270),
                            (600, SCREEN_HEIGHT - 270), (850, SCREEN_HEIGHT - 210), (950, SCREEN_HEIGHT - 210),
                            (1150, SCREEN_HEIGHT - 230), (1250, SCREEN_HEIGHT - 230), (1550, SCREEN_HEIGHT - 290),
                            (1650, SCREEN_HEIGHT - 290), (1950, SCREEN_HEIGHT - 260), (2050, SCREEN_HEIGHT - 260),
                            (2350, SCREEN_HEIGHT - 240),
                            # Sur plateformes moyennes
                            (300, SCREEN_HEIGHT - 380), (600, SCREEN_HEIGHT - 410), (900, SCREEN_HEIGHT - 350),
                            (1100, SCREEN_HEIGHT - 390), (1400, SCREEN_HEIGHT - 370), (1700, SCREEN_HEIGHT - 410),
                            (2000, SCREEN_HEIGHT - 380), (2300, SCREEN_HEIGHT - 400),
                        ]
                        for px, py in red_positions:
                            self.collectibles.append(Collectible(px, py, collect_type="kill_ground"))
                    
                    if not self.blue_stars_added:
                        self.blue_stars_added = True
                        blue_positions = [
                            # Sur plateformes hautes
                            (400, SCREEN_HEIGHT - 530), (500, SCREEN_HEIGHT - 530), (750, SCREEN_HEIGHT - 550),
                            (850, SCREEN_HEIGHT - 550), (1050, SCREEN_HEIGHT - 510), (1150, SCREEN_HEIGHT - 510),
                            (1350, SCREEN_HEIGHT - 540), (1450, SCREEN_HEIGHT - 540), (1650, SCREEN_HEIGHT - 520),
                            (1750, SCREEN_HEIGHT - 520), (1950, SCREEN_HEIGHT - 550), (2050, SCREEN_HEIGHT - 550),
                            (2250, SCREEN_HEIGHT - 530), (2350, SCREEN_HEIGHT - 530),
                            # Sur plateformes très hautes
                            (500, SCREEN_HEIGHT - 680), (600, SCREEN_HEIGHT - 680), (850, SCREEN_HEIGHT - 710),
                            (950, SCREEN_HEIGHT - 710), (1250, SCREEN_HEIGHT - 670), (1350, SCREEN_HEIGHT - 670),
                            (1600, SCREEN_HEIGHT - 700), (1700, SCREEN_HEIGHT - 700), (2000, SCREEN_HEIGHT - 680),
                            (2100, SCREEN_HEIGHT - 680), (2350, SCREEN_HEIGHT - 710), (2450, SCREEN_HEIGHT - 710),
                            # Sur plateformes moyennes aussi
                            (350, SCREEN_HEIGHT - 400), (650, SCREEN_HEIGHT - 420), (950, SCREEN_HEIGHT - 360),
                            (1150, SCREEN_HEIGHT - 400), (1450, SCREEN_HEIGHT - 380), (1750, SCREEN_HEIGHT - 420),
                            (2050, SCREEN_HEIGHT - 390),
                        ]
                        for px, py in blue_positions:
                            self.collectibles.append(Collectible(px, py, collect_type="kill_flying"))
        
        # Mettre à jour les collectibles
        for collectible in self.collectibles:
            collectible.update()
    
    def draw(self, screen, camera_x=0):
        """Dessine tous les éléments du niveau avec décalage de caméra"""
        view_w = screen.get_width()
        # Dessiner les plateformes avec décalage de caméra
        for platform in self.platforms:
            if platform.rect.right - camera_x > 0 and platform.rect.left - camera_x < view_w:
                # Sauvegarder la position originale
                old_x = platform.rect.x
                platform.rect.x -= camera_x
                platform.draw(screen)
                platform.rect.x = old_x  # Restaurer
        
        # Dessiner les collectibles avec décalage de caméra (ou animation de collecte)
        for collectible in self.collectibles:
            in_view = collectible.rect.right - camera_x > 0 and collectible.rect.left - camera_x < view_w
            has_anim = collectible.collected and collectible.collect_particles
            if in_view or has_anim:
                old_x = collectible.rect.x
                collectible.rect.x -= camera_x
                collectible.draw(screen, camera_x)
                collectible.rect.x = old_x
        
        # Dessiner les ennemis avec décalage de caméra
        for enemy in self.enemies:
            if enemy.rect.right - camera_x > 0 and enemy.rect.left - camera_x < view_w:
                old_x = enemy.rect.x
                enemy.rect.x -= camera_x
                enemy.draw(screen)
                enemy.rect.x = old_x
        
        # Dessiner le boss si présent - TOUJOURS en haut à droite de l'écran (fixe)
        if self.boss and self.level_type == "boss":
            # Le boss reste en haut à droite, visible tout le temps
            old_x, old_y = self.boss.rect.x, self.boss.rect.y
            self.boss.rect.x = view_w - 120
            self.boss.rect.y = 60
            self.boss.draw(screen)
            self.boss.rect.x, self.boss.rect.y = old_x, old_y
        
        # Dessiner les checkpoints (petits drapeaux verts)
        if self.checkpoints:
            for cx, cy in self.checkpoints:
                cp_x = cx - camera_x
                if -50 < cp_x < view_w + 50:
                    pygame.draw.circle(screen, GREEN, (int(cp_x), int(cy)), 15)
                    pygame.draw.circle(screen, BLACK, (int(cp_x), int(cy)), 15, 2)
        
        # Dessiner la zone de fin (drapeau) - PAS pour le niveau boss (manche 5)
        if self.level_type != "boss":
            flag_pole_x = self.end_x - camera_x
            flag_pole_y = SCREEN_HEIGHT - 150
            flag_pole_height = 100
            
            pygame.draw.line(screen, (139, 69, 19),  # Marron
                             (flag_pole_x, flag_pole_y),
                             (flag_pole_x, flag_pole_y + flag_pole_height), 5)
            
            flag_width = 40
            flag_height = 30
            flag_rect = pygame.Rect(flag_pole_x + 5, flag_pole_y, flag_width, flag_height)
            
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
            
            font = pygame.font.Font(None, 24)
            text = font.render("GOAL", True, BLACK)
            text_rect = text.get_rect(center=(flag_rect.centerx, flag_rect.centery))
            screen.blit(text, text_rect)
    
    def check_boss_timeout(self):
        """Vérifie si le timer du boss (3min15) est écoulé"""
        if self.level_type == "boss" and hasattr(self, 'boss_start_time') and self.boss_start_time is not None:
            elapsed_ms = pygame.time.get_ticks() - self.boss_start_time
            elapsed_seconds = elapsed_ms / 1000.0
            # 3min15 = 195 secondes
            if elapsed_seconds >= 195:
                return True  # Temps écoulé = défaite
        return False
    
    def check_level_complete(self, player):
        """Vérifie si le joueur a gagné"""
        if self.level_type == "boss":
            # Manche 5 : victoire si le boss explose (tous les ennemis tués avant 3min15)
            if not self.boss:
                return False  # Pas de boss = pas de victoire possible
            
            # VICTOIRE : Si le boss explose (tous les ennemis tués avant la fin des phases)
            if self.boss.exploding:
                return True  # Le boss explose = victoire
            
            # Ne pas considérer la victoire si le boss n'a pas encore commencé à spawner
            # (phase 1, aucun ennemi spawné)
            if self.boss.phase == 1 and self.boss.phase_spawned == 0:
                return False  # Le boss n'a pas encore commencé
            
            # Vérifier si toutes les phases sont terminées (phase > 3 signifie que les 3 phases sont complètes)
            if self.boss.phase > 3:
                # Toutes les phases terminées : vérifier qu'il n'y a plus d'ennemis
                alive_enemies = [e for e in self.enemies if e.alive]
                if len(alive_enemies) == 0:
                    return True  # Toutes les phases terminées ET tous les ennemis tués = victoire
            
            # Le timeout est géré par check_boss_timeout() dans game.py
            return False  # Pas encore gagné
        else:
            return player.rect.right >= self.end_x
    
    def check_checkpoint(self, player):
        """Vérifie si le joueur touche un checkpoint et met à jour last_checkpoint"""
        if not self.checkpoints:
            return
        for i, (cx, cy) in enumerate(self.checkpoints):
            if i in player.checkpoints_reached:
                continue
            if (player.rect.centerx >= cx - 40 and player.rect.centerx <= cx + 40 and
                abs(player.rect.centery - cy) < 80):
                player.checkpoints_reached.append(i)
                player.last_checkpoint = (cx, cy)
                break

