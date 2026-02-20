"""
Classe des ennemis (Robots patrouilleurs)
"""
import pygame
from config import *

class Enemy:
    def __init__(self, x, y, platform_left, platform_right, is_1v1=False, flying=False):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.platform_left = platform_left
        self.platform_right = platform_right
        self.speed = ENEMY_SPEED * 1.5 if is_1v1 else ENEMY_SPEED  # Plus rapide en mode 1v1
        self.direction = 1  # 1 = droite, -1 = gauche
        self.color = RED
        self.alive = True
        self.is_1v1 = is_1v1  # Mode course contre le joueur
        self.flying = flying  # Ennemi volant qui peut se déplacer en l'air
        self.animation_frame = 0  # Pour les animations
        self.walk_animation = 0  # Animation de marche
        self.vertical_speed = 0  # Pour les ennemis volants
        self.flying_range_y = (y - 100, y + 100) if flying else None  # Portée verticale pour les volants
        
    def update(self, platforms, player=None):
        """Met à jour la position de l'ennemi"""
        if not self.alive:
            return
        
        # Animation de marche
        self.animation_frame += 0.2
        self.walk_animation = int(self.animation_frame) % 4  # 4 frames d'animation
        
        # Ennemis volants : mouvement en 8 (horizontal + vertical)
        if self.flying:
            # Mouvement horizontal
            self.rect.x += self.speed * self.direction
            
            # Mouvement vertical (oscillation)
            self.vertical_speed += 0.1 * (1 if self.direction > 0 else -1)
            if abs(self.vertical_speed) > 2:
                self.vertical_speed *= -1
            
            self.rect.y += int(self.vertical_speed)
            
            # Limiter la portée verticale
            if self.flying_range_y:
                if self.rect.y < self.flying_range_y[0]:
                    self.rect.y = self.flying_range_y[0]
                    self.vertical_speed *= -1
                elif self.rect.y > self.flying_range_y[1]:
                    self.rect.y = self.flying_range_y[1]
                    self.vertical_speed *= -1
            
            # Changer de direction aux limites horizontales
            if self.rect.right >= self.platform_right or self.rect.left <= self.platform_left:
                self.direction *= -1
            
            # Ne pas vérifier les collisions avec les plateformes (volant)
            return
        
        # Mode 1v1 : l'ennemi court vers la fin (gauche)
        if self.is_1v1:
            self.rect.x -= self.speed
            # Si l'ennemi atteint la fin avant le joueur, c'est une défaite
            if self.rect.right <= 0:
                return  # L'ennemi a gagné
        else:
            # Mode normal : patrouille
            self.rect.x += self.speed * self.direction
            
            # Vérifier les limites de la plateforme
            if self.rect.right >= self.platform_right or self.rect.left <= self.platform_left:
                self.direction *= -1
        
        # Vérifier collision avec les plateformes (pour éviter de tomber)
        on_platform = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                on_platform = True
                # Si l'ennemi touche un bord de plateforme, changer de direction
                if self.rect.right >= platform.rect.right:
                    self.direction = -1
                elif self.rect.left <= platform.rect.left:
                    self.direction = 1
                break
        
        # Si l'ennemi n'est plus sur une plateforme, le repositionner
        if not on_platform:
            # Trouver la plateforme la plus proche
            for platform in platforms:
                if platform.rect.left <= self.rect.centerx <= platform.rect.right:
                    self.rect.bottom = platform.rect.top
                    break
    
    def check_collision_with_player(self, player):
        """Vérifie la collision avec le joueur"""
        if not self.alive:
            return False, False  # (collision, écrasé)
        
        if self.rect.colliderect(player.rect):
            # Bonus actif : TOUCHER un ennemi volant = il est écrasé (facile!)
            has_jump_bonus = getattr(player, 'jump_bonus_timer', 0) > 0
            if has_jump_bonus and self.flying:
                return True, True  # Écrasé en l'air - juste en touchant!
            
            # Écrasement normal : joueur tombe sur l'ennemi (sol ou volant)
            if player.velocity_y > 0 and player.rect.bottom < self.rect.bottom + 15:
                return True, True  # Écrasé par le dessus
            
            # Collision normale (perte de vie)
            return True, False
        
        return False, False
    
    def draw(self, screen):
        """Dessine l'ennemi comme un personnage méchant style pixel art"""
        if not self.alive:
            return
        
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height
        
        # Pour les ennemis volants, ajouter des ailes
        if self.flying:
            # Ailes animées (oscillent avec l'animation)
            wing_offset = int(3 * (self.animation_frame % 2))
            # Aile gauche
            pygame.draw.ellipse(screen, PURPLE, 
                              (x - 8, y + h // 2 - 5, 12, 8))
            # Aile droite
            pygame.draw.ellipse(screen, PURPLE,
                              (x + w - 4, y + h // 2 - 5, 12, 8))
        
        # Corps principal (forme de blob arrondi, couleur rouge/mauve)
        body_radius = min(w, h) // 2 - 2
        body_center = (x + w // 2, y + h // 2 + 5)
        pygame.draw.circle(screen, self.color, body_center, body_radius)
        pygame.draw.circle(screen, BLACK, body_center, body_radius, 2)
        
        # Tête (cercle plus petit)
        head_radius = body_radius - 3
        head_center = (x + w // 2, y + head_radius + 5)
        pygame.draw.circle(screen, self.color, head_center, head_radius)
        pygame.draw.circle(screen, BLACK, head_center, head_radius, 2)
        
        # Petites cornes au lieu d'antennes (pour le look méchant)
        horn_length = 6
        horn_y_start = head_center[1] - head_radius
        # Corne gauche
        pygame.draw.line(screen, DARK_GRAY,
                        (head_center[0] - 4, horn_y_start),
                        (head_center[0] - 6, horn_y_start - horn_length), 2)
        # Corne droite
        pygame.draw.line(screen, DARK_GRAY,
                        (head_center[0] + 4, horn_y_start),
                        (head_center[0] + 6, horn_y_start - horn_length), 2)
        
        # Yeux méchants (rouges)
        eye_size = 4
        eye_y = head_center[1] - 2
        pygame.draw.circle(screen, RED, (head_center[0] - 4, eye_y), eye_size)
        pygame.draw.circle(screen, RED, (head_center[0] + 4, eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (head_center[0] - 4, eye_y), eye_size, 1)
        pygame.draw.circle(screen, BLACK, (head_center[0] + 4, eye_y), eye_size, 1)
        # Pupilles blanches
        pygame.draw.circle(screen, WHITE, (head_center[0] - 4, eye_y), 1)
        pygame.draw.circle(screen, WHITE, (head_center[0] + 4, eye_y), 1)
        
        # Bouche méchante (arc inversé)
        mouth_y = head_center[1] + 3
        pygame.draw.arc(screen, BLACK,
                       (head_center[0] - 6, mouth_y, 12, 8),
                       3.14, 6.28, 2)
        
        # Petites jambes avec animation de marche
        leg_y = y + h - 5
        leg_offset = int(2 * (self.walk_animation % 2)) - 1  # Animation de marche (-1 ou 1)
        leg_left_x = x + w // 2 - 4 + (leg_offset if self.direction > 0 else -leg_offset)
        leg_right_x = x + w // 2 + 4 - (leg_offset if self.direction > 0 else -leg_offset)
        pygame.draw.circle(screen, self.color, (leg_left_x, leg_y), 3)
        pygame.draw.circle(screen, self.color, (leg_right_x, leg_y), 3)
        pygame.draw.circle(screen, BLACK, (leg_left_x, leg_y), 3, 1)
        pygame.draw.circle(screen, BLACK, (leg_right_x, leg_y), 3, 1)
        
        # Animation des yeux (clignotement)
        eye_blink = int(self.animation_frame * 0.5) % 20 < 1  # Clignote toutes les 20 frames
        if not eye_blink:
            # Yeux normaux (déjà dessinés plus haut)
            pass
        else:
            # Yeux fermés (ligne horizontale)
            pygame.draw.line(screen, BLACK, 
                           (head_center[0] - 6, eye_y),
                           (head_center[0] - 2, eye_y), 2)
            pygame.draw.line(screen, BLACK,
                           (head_center[0] + 2, eye_y),
                           (head_center[0] + 6, eye_y), 2)

