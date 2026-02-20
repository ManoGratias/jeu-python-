"""
Classe des objets collectibles (Étoiles jaunes / Shurikens)
"""
import pygame
import math
import random
from config import *

class Collectible:
    """Étoile jaune = +vitesse. Étoile cyan (type='jump') = +sauts. Étoile rouge (type='kill_ground') = bouclier tuer ennemis au sol 3s. Étoile bleue (type='kill_flying') = bouclier tuer ennemis volants 3s."""
    def __init__(self, x, y, collect_type="speed"):
        self.rect = pygame.Rect(x, y, COLLECTIBLE_SIZE, COLLECTIBLE_SIZE)
        self.collected = False
        self.collect_type = collect_type  # "speed" (jaune), "jump" (cyan), "kill_ground" (rouge), ou "kill_flying" (bleu)
        if collect_type == "speed":
            self.color = YELLOW
        elif collect_type == "jump":
            self.color = CYAN
        elif collect_type == "kill_ground":
            self.color = RED
        elif collect_type == "kill_flying":
            self.color = BLUE
        else:
            self.color = YELLOW
        self.animation_offset = 0
        # Animation de collecte
        self.collect_particles = []
        self.collect_timer = 0
        self.collect_duration = 25  # ~0.4 sec d'animation
        
    def update(self):
        """Met à jour l'animation"""
        if not self.collected:
            self.animation_offset += 0.12
        else:
            # Mettre à jour les particules de collecte
            self.collect_timer += 1
            for p in self.collect_particles[:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.3
                p["life"] -= 1
                p["size"] = max(1, p["size"] - 0.3)
                if p["life"] <= 0:
                    self.collect_particles.remove(p)
    
    def _create_collect_particles(self, center_x, center_y):
        """Crée les particules d'explosion à la collecte"""
        if self.collect_type == "speed":
            colors = [YELLOW, ORANGE, (255, 255, 150)]
        elif self.collect_type == "jump":
            colors = [CYAN, (100, 200, 255), (150, 230, 255)]
        elif self.collect_type == "kill_ground":
            colors = [RED, (255, 100, 100), (255, 150, 150)]
        elif self.collect_type == "kill_flying":
            colors = [BLUE, (100, 150, 255), (150, 200, 255)]
        else:
            colors = [YELLOW, ORANGE, (255, 255, 150)]
        for _ in range(16):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.collect_particles.append({
                "x": center_x,
                "y": center_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 4,
                "size": random.randint(4, 10),
                "color": random.choice(colors),
                "life": random.randint(15, 25),
            })
    
    def check_collision(self, player):
        """Vérifie si le joueur passe sur l'étoile et la récupère (disparaît)"""
        if self.collected:
            return False
        # Zone large : collision rect OU proximité du centre du joueur
        margin = 20
        hit = pygame.Rect(
            self.rect.x - margin, self.rect.y - margin,
            self.rect.width + margin * 2, self.rect.height + margin * 2
        )
        player_center = (player.rect.centerx, player.rect.centery)
        star_center = (self.rect.centerx, self.rect.centery)
        dist = math.sqrt((player_center[0] - star_center[0])**2 + (player_center[1] - star_center[1])**2)
        if hit.colliderect(player.rect) or dist < 45:
            self.collected = True
            center_x = self.rect.centerx
            center_y = self.rect.centery - int(3 * abs(math.sin(self.animation_offset)))
            self._create_collect_particles(center_x, center_y)
            self.collect_timer = 0
            return True
        return False
    
    def draw(self, screen, camera_x=0):
        """Dessine l'étoile ou l'animation de collecte (camera_x pour coordonnées écran)"""
        if self.collected:
            # Dessiner l'animation de collecte (particules en coordonnées écran)
            for p in self.collect_particles:
                alpha = min(255, int(255 * p["life"] / 15))
                s = pygame.Surface((int(p["size"] * 2), int(p["size"] * 2)))
                s.fill(p["color"])
                s.set_alpha(alpha)
                sx = int(p["x"] - camera_x - p["size"])
                sy = int(p["y"] - p["size"])
                screen.blit(s, (sx, sy))
            return
        
        # Animation de flottement + pulsation
        y_offset = int(4 * math.sin(self.animation_offset))
        pulse = 1 + 0.15 * math.sin(self.animation_offset * 1.5)
        
        center_x = self.rect.centerx
        center_y = self.rect.centery - y_offset
        
        size = int((self.rect.width // 2) * pulse)
        rotation = self.animation_offset * 2.5
        
        glow_color = self.color
        glow_surf = pygame.Surface((size * 4, size * 4))
        glow_surf.set_alpha(50)
        pygame.draw.circle(glow_surf, glow_color, (size * 2, size * 2), size + 8)
        screen.blit(glow_surf, (center_x - size * 2, center_y - size * 2))
        
        points = []
        for i in range(8):
            angle = (i * math.pi / 4) + rotation
            r = size if i % 2 == 0 else size // 2
            px = center_x + r * math.cos(angle)
            py = center_y + r * math.sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(screen, self.color, points)
        if self.collect_type == "speed":
            border_color = (255, 220, 0)
            center_color = ORANGE
        elif self.collect_type == "jump":
            border_color = (150, 230, 255)
            center_color = (50, 150, 255)
        elif self.collect_type == "kill_ground":
            border_color = (255, 150, 150)
            center_color = (255, 100, 100)
        elif self.collect_type == "kill_flying":
            border_color = (100, 150, 255)
            center_color = (50, 100, 255)
        else:
            border_color = (255, 220, 0)
            center_color = ORANGE
        pygame.draw.polygon(screen, border_color, points, 1)
        pygame.draw.polygon(screen, BLACK, points, 2)
        pygame.draw.circle(screen, center_color, (int(center_x), int(center_y)), 4)
        pygame.draw.circle(screen, BLACK, (int(center_x), int(center_y)), 4, 1)
