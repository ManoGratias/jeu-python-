"""
Classe du Boss Final - 3 phases : sol (10), air (10), les deux
Chaque phase terminée = boss perd 1 vie. Boss a 5 vies au total.
"""
import pygame
import random
from config import *
from enemy import Enemy

class Boss:
    def __init__(self, x, y):
        self.width = 80
        self.height = 100
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = RED
        self.alive = True
        self.health = 3
        self.max_health = 3
        self.animation_frame = 0
        self.spawn_timer = 0
        self.spawn_interval = 8  # Frames (~0.13 sec) - apparition BEAUCOUP plus rapide
        
        # Phases : 1=sol uniquement, 2=air uniquement, 3=les deux
        self.phase = 1
        self.phase_spawned = 0
        self.phase_goal = 15  # 15 ennemis par phase (15-20)
        self.phase_ground_done = False  # Pour phase 3 : sol terminé
        self.phase_flying_done = False  # Pour phase 3 : air terminé
        self.exploding = False  # Animation d'explosion
        self.explosion_timer = 0
        
    def update(self, platforms, player=None, level=None):
        """Le boss reste en place et lance des ennemis selon la phase"""
        if self.exploding:
            self.explosion_timer += 1
            return
        
        if not self.alive:
            return
        
        self.animation_frame += 0.1
        
        if not level or level.enemies is None or self.health <= 0:
            return
        
        # Nettoyer les ennemis morts
        level.enemies = [e for e in level.enemies if e.alive]
        
        # Vérifier si la phase est terminée (tous les ennemis de la phase sont morts)
        if self._phase_complete(level):
            self._advance_phase(level)
            return
        
        # VICTOIRE : Le boss explose SEULEMENT si toutes les 3 phases sont complétées ET tous les ennemis tués
        # Phase > 3 signifie que les 3 phases (1, 2, 3) sont toutes complétées
        if self.phase > 3 and len(level.enemies) == 0:
            # Toutes les phases terminées ET tous les ennemis tués = victoire
            self.exploding = True
            self.explosion_timer = 0
            self.alive = False
            return
        
        # Spawn selon la phase
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            if self._can_spawn():
                self._spawn_minion(level)
                self.phase_spawned += 1
    
    def _phase_complete(self, level):
        """Phase terminée si : on a spawné le goal ET plus d'ennemis vivants"""
        if self.phase_spawned < self.phase_goal:
            return False
        # Phase 3 : 15 sol + 15 air = 30 total
        if self.phase == 3:
            return len(level.enemies) == 0
        return len(level.enemies) == 0
    
    def _can_spawn(self):
        """Peut-on encore spawner pour cette phase ?"""
        if self.phase == 1:
            return self.phase_spawned < 15  # 15 ennemis au sol
        if self.phase == 2:
            return self.phase_spawned < 15  # 15 ennemis volants
        if self.phase == 3:
            return self.phase_spawned < 30  # 15 sol + 15 air = 30 total
        return False
    
    def _advance_phase(self, level):
        """Passe à la phase suivante, boss perd 1 vie"""
        self.health -= 1
        self.phase += 1
        self.phase_spawned = 0
        self.phase_ground_done = False
        
        # Si toutes les phases sont complétées (phase > 3), le boss explose
        if self.phase > 3:
            # Toutes les phases terminées : vérifier qu'il n'y a plus d'ennemis
            alive_enemies = [e for e in level.enemies if e.alive]
            if len(alive_enemies) == 0:
                # Toutes les phases terminées ET tous les ennemis tués = explosion
                self.exploding = True
                self.explosion_timer = 0
                self.alive = False
            # Sinon, le boss reste vivant jusqu'à ce que tous les ennemis soient tués
        elif self.health <= 0:
            # Si le boss n'a plus de vies mais qu'il reste des phases, le boss reste vivant
            # (les phases doivent être complétées pour gagner)
            pass
        self.phase_flying_done = False
        
        if self.phase == 2:
            self.phase_goal = 15  # 15 volants
        elif self.phase == 3:
            self.phase_goal = 30  # 15 sol + 15 air = 30 total
    
    def _spawn_minion(self, level):
        """Spawn un ennemi selon la phase"""
        level_end_x = level.end_x + 50 if level else SCREEN_WIDTH * 2 - 50
        ground_y = SCREEN_HEIGHT - 50 - 35
        
        spawn_x = random.randint(100, int(self.rect.left - 50)) if self.rect.left > 200 else random.randint(100, 800)
        spawn_x = max(80, min(spawn_x, level_end_x - 80))
        platform_left = max(0, spawn_x - 100)
        platform_right = min(level_end_x, spawn_x + 100)
        
        if self.phase == 1:
            # Phase 1 : uniquement au sol
            e = Enemy(spawn_x, ground_y, platform_left, platform_right)
        elif self.phase == 2:
            # Phase 2 : uniquement en l'air
            spawn_y = random.randint(200, SCREEN_HEIGHT - 200)
            e = Enemy(spawn_x, spawn_y, platform_left, platform_right, flying=True)
        else:
            # Phase 3 : alterner sol et air
            if self.phase_spawned % 2 == 0:
                e = Enemy(spawn_x, ground_y, platform_left, platform_right)
            else:
                spawn_y = random.randint(200, SCREEN_HEIGHT - 200)
                e = Enemy(spawn_x, spawn_y, platform_left, platform_right, flying=True)
        level.enemies.append(e)
    
    def take_damage(self):
        """Le boss prend des dégâts"""
        self.health -= 1
        if self.health <= 0:
            self.alive = False
    
    def check_collision_with_player(self, player):
        """Vérifie la collision avec le joueur"""
        if not self.alive:
            return False, False
        
        if self.rect.colliderect(player.rect):
            if player.velocity_y > 0 and player.rect.bottom < self.rect.bottom + 15:
                return True, True  # Écrasé
            else:
                return True, False  # Collision normale (perte de vie)
        
        return False, False
    
    def draw(self, screen):
        """Dessine le grand robot boss"""
        if self.exploding:
            # Animation d'explosion
            self._draw_explosion(screen)
            return
        
        if not self.alive:
            return
        
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height
        
        body_rect = pygame.Rect(x + 10, y + 20, w - 20, h - 30)
        pygame.draw.rect(screen, self.color, body_rect)
        pygame.draw.rect(screen, BLACK, body_rect, 3)
        
        head_size = 35
        head_rect = pygame.Rect(x + (w - head_size) // 2, y, head_size, head_size)
        pygame.draw.rect(screen, self.color, head_rect)
        pygame.draw.rect(screen, BLACK, head_rect, 3)
        
        eye_size = 6
        eye_y = y + 12
        eye_color = RED if int(self.animation_frame) % 2 == 0 else YELLOW
        pygame.draw.circle(screen, eye_color, (x + w // 2 - 8, eye_y), eye_size)
        pygame.draw.circle(screen, eye_color, (x + w // 2 + 8, eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (x + w // 2 - 8, eye_y), eye_size, 2)
        pygame.draw.circle(screen, BLACK, (x + w // 2 + 8, eye_y), eye_size, 2)
        pygame.draw.circle(screen, BLACK, (x + w // 2 - 8, eye_y), 3)
        pygame.draw.circle(screen, BLACK, (x + w // 2 + 8, eye_y), 3)
        
        horn_points = [
            (x + w // 2, y - 5),
            (x + w // 2 - 5, y - 15),
            (x + w // 2 + 5, y - 15)
        ]
        pygame.draw.polygon(screen, DARK_GRAY, horn_points)
        pygame.draw.polygon(screen, BLACK, horn_points, 2)
        
        arm_width, arm_height = 8, 40
        pygame.draw.rect(screen, self.color, (x - 3, y + 25, arm_width, arm_height))
        pygame.draw.rect(screen, BLACK, (x - 3, y + 25, arm_width, arm_height), 2)
        pygame.draw.rect(screen, self.color, (x + w - 5, y + 25, arm_width, arm_height))
        pygame.draw.rect(screen, BLACK, (x + w - 5, y + 25, arm_width, arm_height), 2)
        
        leg_width, leg_height = 12, 25
        pygame.draw.rect(screen, self.color, (x + 15, y + h - leg_height, leg_width, leg_height))
        pygame.draw.rect(screen, BLACK, (x + 15, y + h - leg_height, leg_width, leg_height), 2)
        pygame.draw.rect(screen, self.color, (x + w - 27, y + h - leg_height, leg_width, leg_height))
        pygame.draw.rect(screen, BLACK, (x + w - 27, y + h - leg_height, leg_width, leg_height), 2)
        
        pygame.draw.line(screen, DARK_GRAY, (body_rect.left + 5, body_rect.top + 15), (body_rect.right - 5, body_rect.top + 15), 2)
        pygame.draw.line(screen, DARK_GRAY, (body_rect.left + 5, body_rect.bottom - 15), (body_rect.right - 5, body_rect.bottom - 15), 2)
        
        health_bar_width, health_bar_height = 100, 8
        health_bar_x = x + (w - health_bar_width) // 2
        health_bar_y = y - 25
        pygame.draw.rect(screen, DARK_GRAY, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        health_percentage = self.health / self.max_health
        health_fill_width = int(health_bar_width * health_percentage)
        health_color = GREEN if health_percentage > 0.5 else YELLOW if health_percentage > 0.25 else RED
        pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, health_fill_width, health_bar_height))
        pygame.draw.rect(screen, BLACK, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)
        
        font = pygame.font.Font(None, 20)
        phase_name = ["", "Phase 1: Sol", "Phase 2: Air", "Phase 3: Sol+Air"][min(self.phase, 3)]
        phase_text = font.render(phase_name, True, WHITE)
        screen.blit(phase_text, (x + (w - phase_text.get_width()) // 2, y - 40))
        vies_text = font.render(f"{self.health} vies", True, WHITE)
        screen.blit(vies_text, (x + (w - vies_text.get_width()) // 2, y - 55))
    
    def _draw_explosion(self, screen):
        """Dessine l'animation d'explosion du boss"""
        x, y = self.rect.centerx, self.rect.centery
        explosion_radius = min(200, self.explosion_timer * 3)
        alpha = max(0, 255 - self.explosion_timer * 5)
        
        # Particules d'explosion
        import random
        for i in range(30):
            angle = (i / 30) * 6.28
            dist = explosion_radius * (0.5 + random.random() * 0.5)
            px = x + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            py = y + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            color = random.choice([RED, ORANGE, YELLOW])
            size = random.randint(3, 8)
            pygame.draw.circle(screen, color, (px, py), size)
        
        # Cercle d'explosion principal
        if explosion_radius > 0:
            explosion_surface = pygame.Surface((explosion_radius * 2, explosion_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (255, 100, 0, alpha), (explosion_radius, explosion_radius), explosion_radius)
            screen.blit(explosion_surface, (x - explosion_radius, y - explosion_radius))
