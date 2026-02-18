"""
Configuration du jeu Cyber Jump
"""
import pygame

# Couleurs - Style Pixel Art Fun
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 250)  # Ciel bleu clair (ancien, gardé pour compatibilité)
CLOUD_WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)  # Orange vif
PLATFORM_GREEN = (50, 205, 50)  # Vert des plateformes
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
CYAN = (0, 255, 255)
PURPLE = (186, 85, 211)
PINK = (255, 20, 147)
BLUE = (50, 150, 255)
LIGHT_BLUE = (173, 216, 230)

# Nouvelles couleurs modernes
DARK_PURPLE = (75, 0, 130)  # Violet foncé
MEDIUM_PURPLE = (138, 43, 226)  # Violet moyen
LIGHT_PURPLE = (221, 160, 221)  # Violet clair
GRADIENT_START = (25, 25, 112)  # Bleu nuit foncé
GRADIENT_END = (138, 43, 226)  # Violet
STAR_COLOR = (255, 255, 200)  # Couleur des étoiles

# Paramètres de l'écran
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Paramètres du joueur
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
PLAYER_SPEED = 7  # Vitesse augmentée pour plus de réactivité
PLAYER_JUMP_STRENGTH = -16  # Force de saut augmentée pour un meilleur saut
GRAVITY = 0.9  # Gravité équilibrée
FRICTION = 0.85  # Friction réduite pour un mouvement plus fluide
MAX_FALL_SPEED = 15  # Vitesse de chute maximale

# Paramètres des ennemis
ENEMY_WIDTH = 35
ENEMY_HEIGHT = 35
ENEMY_SPEED = 2

# Paramètres des collectibles
COLLECTIBLE_SIZE = 20

# Paramètres des plateformes
PLATFORM_HEIGHT = 20

# Scores
SCORE_COLLECTIBLE = 50
SCORE_ENEMY = 200

# Fichiers
SCORES_FILE = "scores.json"
LEVEL_FILE = "level.txt"

