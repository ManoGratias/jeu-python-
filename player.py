"""
Classe du joueur (Robot Cyber)
"""
import pygame
from config import *

class Player:
    def __init__(self, x, y, player_id=1):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.lives = 5  # 5 vies au lieu de 3
        self.player_id = player_id
        self.color = LIGHT_BLUE if player_id == 1 else GREEN  # Joueur 2 = vert
        self.jump_count = 0
        self.max_jumps = 2
        self.last_checkpoint = (x, y)  # Point de respawn
        self.checkpoints_reached = []   # Indices des checkpoints franchis
        self.stars_collected = 0        # Étoiles collectées (tous les 5 = +vitesse)
        self.jump_bonus_timer = 0      # Timer pour le bonus de saut (15 secondes = 900 frames)
        self.ground_shield_timer = 0   # Timer pour le bouclier rouge (tuer ennemis au sol) - 3 secondes = 180 frames
        self.flying_shield_timer = 0   # Timer pour le bouclier bleu (tuer ennemis volants) - 3 secondes = 180 frames
        self.boss_level_speed_boost = False  # Boost de vitesse en manche 5
        self.bubbles_timer = 0  # Timer pour l'effet de bulles (3 secondes = 180 frames)
        self.bubbles = []  # Liste des bulles pour l'effet visuel
        
    def get_speed(self):
        """Vitesse actuelle : +2 tous les 5 étoiles, +50% en manche 5"""
        base_speed = PLAYER_SPEED + (self.stars_collected // 5) * 2
        if self.boss_level_speed_boost:
            return int(base_speed * 1.5)  # +50% de vitesse en manche 5
        return base_speed
        
    def update(self, platforms):
        """Met à jour la position du joueur avec la physique améliorée"""
        # Mettre à jour les timers
        if self.jump_bonus_timer > 0:
            self.jump_bonus_timer -= 1
        if self.ground_shield_timer > 0:
            self.ground_shield_timer -= 1
        if self.flying_shield_timer > 0:
            self.flying_shield_timer -= 1
        # Effet de bulles pendant 3 secondes maximum
        if self.bubbles_timer > 0:
            self.bubbles_timer -= 1
            # Mettre à jour les bulles existantes
            import random
            import math
            for bubble in self.bubbles[:]:
                bubble['x'] += bubble['vx']
                bubble['y'] += bubble['vy']
                bubble['vy'] -= 0.3  # Les bulles montent
                bubble['life'] -= 1
                bubble['size'] += 0.2  # Les bulles grossissent
                if bubble['life'] <= 0:
                    self.bubbles.remove(bubble)
            # Ajouter de nouvelles bulles seulement au début (premières frames)
            if self.bubbles_timer > 150:  # Seulement pendant les premières 0.5 secondes
                if len(self.bubbles) < 8 and random.random() < 0.3:  # Moins de bulles
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1, 2)
                    self.bubbles.append({
                        'x': self.rect.centerx + random.randint(-20, 20),
                        'y': self.rect.centery + random.randint(-20, 20),
                        'vx': math.cos(angle) * speed,
                        'vy': -random.uniform(2, 4),
                        'size': random.randint(5, 12),
                        'life': random.randint(30, 60),
                        'alpha': random.randint(150, 255)
                    })
            # Quand le timer arrive à 0, nettoyer toutes les bulles
            if self.bubbles_timer == 0:
                self.bubbles = []
        
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
            self.reset_to_checkpoint()
    
    def reset_to_checkpoint(self):
        """Réinitialise au dernier checkpoint"""
        x, y = self.last_checkpoint
        self.reset_position(x, y)
    
    def reset_position(self, x=50, y=100):
        """Réinitialise la position du joueur"""
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_count = 0
    
    def move_left(self):
        """Déplace le joueur vers la gauche"""
        self.velocity_x = -self.get_speed()
    
    def move_right(self):
        """Déplace le joueur vers la droite"""
        self.velocity_x = self.get_speed()
    
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
        
        # Effet visuel du bonus de saut (halo cyan pulsant)
        if self.jump_bonus_timer > 0:
            import math
            pulse = 1 + 0.3 * math.sin(self.jump_bonus_timer * 0.2)
            halo_radius = int(body_radius * pulse + 8)
            # Halo cyan semi-transparent
            halo_surf = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo_surf, (0, 255, 255, 100), (halo_radius, halo_radius), halo_radius)
            screen.blit(halo_surf, (body_center[0] - halo_radius, body_center[1] - halo_radius))
            # Bordure cyan
            pygame.draw.circle(screen, CYAN, body_center, halo_radius, 2)
        
        # Effet visuel des boucliers (halo rouge ou bleu)
        if self.ground_shield_timer > 0:
            import math
            pulse = 1 + 0.2 * math.sin(self.ground_shield_timer * 0.15)
            shield_radius = int(body_radius * pulse + 10)
            # Halo rouge semi-transparent
            shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (255, 100, 100, 120), (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surf, (body_center[0] - shield_radius, body_center[1] - shield_radius))
            # Bordure rouge
            pygame.draw.circle(screen, RED, body_center, shield_radius, 2)
        
        if self.flying_shield_timer > 0:
            import math
            pulse = 1 + 0.2 * math.sin(self.flying_shield_timer * 0.15)
            shield_radius = int(body_radius * pulse + 10)
            # Halo bleu semi-transparent
            shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 150, 255, 120), (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surf, (body_center[0] - shield_radius, body_center[1] - shield_radius))
            # Bordure bleue
            pygame.draw.circle(screen, BLUE, body_center, shield_radius, 2)
        
        # Effet de bulles pendant 3 secondes maximum
        if self.bubbles_timer > 0:
            import math
            for bubble in self.bubbles:
                alpha = min(255, int(255 * bubble['life'] / 60))
                bubble_surf = pygame.Surface((int(bubble['size'] * 2), int(bubble['size'] * 2)), pygame.SRCALPHA)
                pygame.draw.circle(bubble_surf, (200, 230, 255, alpha), 
                                 (int(bubble['size']), int(bubble['size'])), int(bubble['size']))
                screen.blit(bubble_surf, (int(bubble['x'] - bubble['size']), int(bubble['y'] - bubble['size'])))
                # Bordure blanche
                pygame.draw.circle(screen, (255, 255, 255, alpha), 
                                  (int(bubble['x']), int(bubble['y'])), int(bubble['size']), 1)
        
        # Indicateur de double saut (petite flèche verte)
        if self.jump_count < self.max_jumps:
            arrow_points = [
                (x + w + 3, y - 5),
                (x + w + 8, y - 10),
                (x + w + 13, y - 5)
            ]
            pygame.draw.polygon(screen, GREEN, arrow_points)

