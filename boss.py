"""
Classe du Boss Final - Grand Robot
"""
import pygame
from config import *

class Boss:
    def __init__(self, x, y):
        # Boss plus grand que les ennemis normaux
        self.width = 80
        self.height = 100
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = ENEMY_SPEED * 2  # Plus rapide que les ennemis normaux
        self.color = RED
        self.alive = True
        self.health = 3  # Le boss a plusieurs vies
        self.max_health = 3
        self.animation_frame = 0
        
    def update(self, platforms, player=None):
        """Met à jour la position du boss"""
        if not self.alive:
            return
        
        # Le boss court vers la fin (gauche) en mode 1v1
        self.rect.x -= self.speed
        
        # Animation
        self.animation_frame += 0.1
        
        # Si le boss atteint la fin avant le joueur, c'est une défaite
        if self.rect.right <= 0:
            return  # Le boss a gagné
    
    def take_damage(self):
        """Le boss prend des dégâts"""
        self.health -= 1
        if self.health <= 0:
            self.alive = False
    
    def check_collision_with_player(self, player):
        """Vérifie la collision avec le joueur"""
        if not self.alive:
            return False, False  # (collision, écrasé)
        
        if self.rect.colliderect(player.rect):
            # Si le joueur tombe sur le boss (écrasement)
            if player.velocity_y > 0 and player.rect.bottom < self.rect.bottom + 15:
                return True, True  # Écrasé
            else:
                return True, False  # Collision normale (perte de vie)
        
        return False, False
    
    def draw(self, screen):
        """Dessine le grand robot boss"""
        if not self.alive:
            return
        
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height
        
        # Corps principal du boss (plus grand)
        body_rect = pygame.Rect(x + 10, y + 20, w - 20, h - 30)
        pygame.draw.rect(screen, self.color, body_rect)
        pygame.draw.rect(screen, BLACK, body_rect, 3)
        
        # Tête du boss (grande)
        head_size = 35
        head_rect = pygame.Rect(x + (w - head_size) // 2, y, head_size, head_size)
        pygame.draw.rect(screen, self.color, head_rect)
        pygame.draw.rect(screen, BLACK, head_rect, 3)
        
        # Yeux menaçants du boss (plus grands)
        eye_size = 6
        eye_y = y + 12
        # Animation des yeux (clignotement)
        eye_color = RED if int(self.animation_frame) % 2 == 0 else YELLOW
        pygame.draw.circle(screen, eye_color, (x + w // 2 - 8, eye_y), eye_size)
        pygame.draw.circle(screen, eye_color, (x + w // 2 + 8, eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (x + w // 2 - 8, eye_y), eye_size, 2)
        pygame.draw.circle(screen, BLACK, (x + w // 2 + 8, eye_y), eye_size, 2)
        # Pupilles
        pygame.draw.circle(screen, BLACK, (x + w // 2 - 8, eye_y), 3)
        pygame.draw.circle(screen, BLACK, (x + w // 2 + 8, eye_y), 3)
        
        # Corne centrale du boss
        horn_points = [
            (x + w // 2, y - 5),
            (x + w // 2 - 5, y - 15),
            (x + w // 2 + 5, y - 15)
        ]
        pygame.draw.polygon(screen, DARK_GRAY, horn_points)
        pygame.draw.polygon(screen, BLACK, horn_points, 2)
        
        # Bras du boss (grands)
        arm_width = 8
        arm_height = 40
        # Bras gauche
        left_arm = pygame.Rect(x - 3, y + 25, arm_width, arm_height)
        pygame.draw.rect(screen, self.color, left_arm)
        pygame.draw.rect(screen, BLACK, left_arm, 2)
        # Bras droit
        right_arm = pygame.Rect(x + w - 5, y + 25, arm_width, arm_height)
        pygame.draw.rect(screen, self.color, right_arm)
        pygame.draw.rect(screen, BLACK, right_arm, 2)
        
        # Jambes du boss (grandes)
        leg_width = 12
        leg_height = 25
        # Jambe gauche
        left_leg = pygame.Rect(x + 15, y + h - leg_height, leg_width, leg_height)
        pygame.draw.rect(screen, self.color, left_leg)
        pygame.draw.rect(screen, BLACK, left_leg, 2)
        # Jambe droite
        right_leg = pygame.Rect(x + w - 27, y + h - leg_height, leg_width, leg_height)
        pygame.draw.rect(screen, self.color, right_leg)
        pygame.draw.rect(screen, BLACK, right_leg, 2)
        
        # Détails sur le corps (lignes)
        pygame.draw.line(screen, DARK_GRAY,
                        (body_rect.left + 5, body_rect.top + 15),
                        (body_rect.right - 5, body_rect.top + 15), 2)
        pygame.draw.line(screen, DARK_GRAY,
                        (body_rect.left + 5, body_rect.bottom - 15),
                        (body_rect.right - 5, body_rect.bottom - 15), 2)
        
        # Barre de vie du boss (en haut)
        health_bar_width = 100
        health_bar_height = 8
        health_bar_x = x + (w - health_bar_width) // 2
        health_bar_y = y - 25
        
        # Fond de la barre de vie
        pygame.draw.rect(screen, DARK_GRAY,
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Barre de vie actuelle
        health_percentage = self.health / self.max_health
        health_fill_width = int(health_bar_width * health_percentage)
        health_color = GREEN if health_percentage > 0.5 else YELLOW if health_percentage > 0.25 else RED
        pygame.draw.rect(screen, health_color,
                        (health_bar_x, health_bar_y, health_fill_width, health_bar_height))
        pygame.draw.rect(screen, BLACK,
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)
        
        # Texte "BOSS" au-dessus
        font = pygame.font.Font(None, 20)
        boss_text = font.render("BOSS", True, RED)
        screen.blit(boss_text, (x + (w - boss_text.get_width()) // 2, y - 40))

