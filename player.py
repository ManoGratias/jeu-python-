"""
Classe du joueur (Robot Cyber)
"""
import pygame
from config import *

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.lives = 5  # 5 vies au lieu de 3
        self.color = LIGHT_BLUE  # Couleur par défaut du joueur
        self.jump_count = 0  # Compteur pour le double saut
        self.max_jumps = 2  # Nombre maximum de sauts (double saut)
        
    def update(self, platforms):
        """Met à jour la position du joueur avec la physique améliorée"""
        # Appliquer la gravité
        self.velocity_y += GRAVITY
        
        # Limiter la vitesse de chute
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED
        
        # Appliquer le mouvement horizontal avec friction
        self.velocity_x *= FRICTION
        if abs(self.velocity_x) < 0.1:
            self.velocity_x = 0
        
        # Sauvegarder la position avant déplacement
        old_x = self.rect.x
        old_y = self.rect.y
        
        # Déplacer horizontalement d'abord
        self.rect.x += int(self.velocity_x)
        
        # Collision horizontale avec les plateformes
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:  # Se déplace vers la droite
                    self.rect.right = platform.rect.left
                    self.velocity_x = 0
                elif self.velocity_x < 0:  # Se déplace vers la gauche
                    self.rect.left = platform.rect.right
                    self.velocity_x = 0
        
        # Déplacer verticalement
        self.rect.y += int(self.velocity_y)
        
        # Collision verticale avec les plateformes
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Calculer les chevauchements
                overlap_top = self.rect.bottom - platform.rect.top
                overlap_bottom = platform.rect.bottom - self.rect.top
                
                # Si on tombe sur une plateforme (par-dessus)
                if overlap_top < overlap_bottom and self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                # Si on touche le dessous d'une plateforme (par-dessous)
                elif overlap_bottom < overlap_top and self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
        
        # Vérification supplémentaire pour détecter si on est au sol (tolérance réduite)
        if not self.on_ground and self.velocity_y >= 0:
            for platform in platforms:
                # Vérifier si le joueur est juste au-dessus d'une plateforme (tolérance de 2 pixels)
                if (self.rect.bottom <= platform.rect.top + 2 and
                    self.rect.bottom >= platform.rect.top - 2 and
                    self.rect.right > platform.rect.left + 2 and
                    self.rect.left < platform.rect.right - 2):
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    break
        
        # Ne plus limiter le joueur à l'écran (la caméra suit maintenant)
        # Le joueur peut se déplacer librement dans le niveau
        
        # Si le joueur tombe en bas de l'écran, perte de vie
        if self.rect.top > SCREEN_HEIGHT:
            self.lives -= 1
            self.reset_position()
    
    def reset_position(self):
        """Réinitialise la position du joueur"""
        self.rect.x = 50
        self.rect.y = 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_count = 0
    
    def move_left(self):
        """Déplace le joueur vers la gauche"""
        self.velocity_x = -PLAYER_SPEED
    
    def move_right(self):
        """Déplace le joueur vers la droite"""
        self.velocity_x = PLAYER_SPEED
    
    def jump(self):
        """Fait sauter le joueur (double saut autorisé)"""
        # Premier saut : doit être au sol
        if self.jump_count == 0:
            if self.on_ground:
                self.velocity_y = PLAYER_JUMP_STRENGTH
                self.jump_count = 1
                self.on_ground = False
        # Double saut : peut être fait en l'air après le premier saut
        elif self.jump_count == 1 and self.jump_count < self.max_jumps:
            self.velocity_y = PLAYER_JUMP_STRENGTH
            self.jump_count = 2
            self.on_ground = False
    
    def draw(self, screen):
        """Dessine le joueur comme un personnage mignon style pixel art"""
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height
        
        # Corps principal (forme de blob arrondi)
        body_radius = min(w, h) // 2 - 2
        body_center = (x + w // 2, y + h // 2 + 5)
        pygame.draw.circle(screen, self.color, body_center, body_radius)
        pygame.draw.circle(screen, BLACK, body_center, body_radius, 2)
        
        # Tête (cercle plus petit au-dessus du corps)
        head_radius = body_radius - 3
        head_center = (x + w // 2, y + head_radius + 5)
        pygame.draw.circle(screen, self.color, head_center, head_radius)
        pygame.draw.circle(screen, BLACK, head_center, head_radius, 2)
        
        # Antennes vertes (comme dans l'image)
        antenna_length = 8
        antenna_y_start = head_center[1] - head_radius
        # Antenne gauche
        pygame.draw.line(screen, GREEN, 
                        (head_center[0] - 5, antenna_y_start),
                        (head_center[0] - 5, antenna_y_start - antenna_length), 2)
        pygame.draw.circle(screen, GREEN, 
                          (head_center[0] - 5, antenna_y_start - antenna_length), 2)
        # Antenne droite
        pygame.draw.line(screen, GREEN,
                        (head_center[0] + 5, antenna_y_start),
                        (head_center[0] + 5, antenna_y_start - antenna_length), 2)
        pygame.draw.circle(screen, GREEN,
                          (head_center[0] + 5, antenna_y_start - antenna_length), 2)
        
        # Yeux mignons (2 cercles)
        eye_size = 4
        eye_y = head_center[1] - 2
        pygame.draw.circle(screen, WHITE, (head_center[0] - 4, eye_y), eye_size)
        pygame.draw.circle(screen, WHITE, (head_center[0] + 4, eye_y), eye_size)
        # Pupilles noires
        pygame.draw.circle(screen, BLACK, (head_center[0] - 4, eye_y), 2)
        pygame.draw.circle(screen, BLACK, (head_center[0] + 4, eye_y), 2)
        
        # Sourire (arc)
        smile_y = head_center[1] + 3
        pygame.draw.arc(screen, BLACK,
                       (head_center[0] - 6, smile_y - 3, 12, 8),
                       0, 3.14, 2)
        
        # Petites jambes (2 cercles en bas)
        leg_y = y + h - 5
        pygame.draw.circle(screen, self.color, (x + w // 2 - 4, leg_y), 3)
        pygame.draw.circle(screen, self.color, (x + w // 2 + 4, leg_y), 3)
        pygame.draw.circle(screen, BLACK, (x + w // 2 - 4, leg_y), 3, 1)
        pygame.draw.circle(screen, BLACK, (x + w // 2 + 4, leg_y), 3, 1)
        
        # Indicateur de double saut (petite flèche verte)
        if self.jump_count < self.max_jumps:
            arrow_points = [
                (x + w + 3, y - 5),
                (x + w + 8, y - 10),
                (x + w + 13, y - 5)
            ]
            pygame.draw.polygon(screen, GREEN, arrow_points)

