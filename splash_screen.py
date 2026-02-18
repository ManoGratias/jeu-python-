"""
Écran d'accueil avec animation du titre
"""
import pygame
import math
import random
from config import *

class SplashScreen:
    def __init__(self, screen):
        self.screen = screen
        self.timer = 0
        self.finished = False
        self.font_title = pygame.font.Font(None, 96)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_press = pygame.font.Font(None, 28)
        
        # Animation du titre
        self.title_scale = 0.0
        self.title_alpha = 0
        self.title_y_offset = 0
        
        # Particules d'étoiles
        self.stars = []
        for _ in range(50):
            self.stars.append({
                'x': pygame.time.get_ticks() % SCREEN_WIDTH + (pygame.time.get_ticks() % 100),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.2, 0.8),
                'twinkle': random.uniform(0, math.pi * 2)
            })
    
    def update(self):
        """Met à jour l'animation"""
        self.timer += 1/60  # 60 FPS
        
        # Animation du titre (apparition et zoom)
        if self.timer < 1.5:
            # Phase 1: Apparition avec zoom
            progress = self.timer / 1.5
            self.title_scale = progress
            self.title_alpha = int(255 * progress)
        elif self.timer < 2.5:
            # Phase 2: Légère oscillation
            self.title_scale = 1.0 + math.sin(self.timer * 3) * 0.05
            self.title_alpha = 255
        else:
            # Phase 3: Stable
            self.title_scale = 1.0
            self.title_alpha = 255
        
        # Animation des étoiles
        for star in self.stars:
            star['x'] += star['speed']
            star['twinkle'] += 0.1
            if star['x'] > SCREEN_WIDTH + 10:
                star['x'] = -10
                star['y'] = random.randint(0, SCREEN_HEIGHT)
    
    def handle_event(self, event):
        """Gère les événements (touche pressée pour passer)"""
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if self.timer > 1.0:  # Permettre de passer après 1 seconde
                self.finished = True
        return self.finished
    
    def draw(self):
        """Dessine l'écran d'accueil"""
        # Fond dégradé violet/bleu nuit
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Dessiner les étoiles
        for star in self.stars:
            alpha = int(128 + 127 * math.sin(star['twinkle']))
            star_surface = pygame.Surface((star['size'] * 2, star['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, (*STAR_COLOR[:3], alpha), 
                             (star['size'], star['size']), star['size'])
            self.screen.blit(star_surface, (int(star['x']) - star['size'], 
                                           int(star['y']) - star['size']))
        
        # Titre avec animation
        title_text = "CYBER JUMP"
        title_surface = self.font_title.render(title_text, True, ORANGE)
        
        # Appliquer le scale et l'alpha
        scaled_width = int(title_surface.get_width() * self.title_scale)
        scaled_height = int(title_surface.get_height() * self.title_scale)
        scaled_title = pygame.transform.scale(title_surface, (scaled_width, scaled_height))
        
        # Créer une surface avec alpha
        title_alpha = pygame.Surface(scaled_title.get_size(), pygame.SRCALPHA)
        title_alpha.fill((255, 255, 255, self.title_alpha))
        title_alpha.blit(scaled_title, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Ombre du titre
        shadow_offset = 5
        shadow_surface = pygame.Surface(scaled_title.get_size(), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, self.title_alpha // 2))
        shadow_surface.blit(scaled_title, (shadow_offset, shadow_offset), 
                          special_flags=pygame.BLEND_RGBA_MULT)
        
        # Position du titre (centré)
        title_x = SCREEN_WIDTH // 2 - scaled_width // 2
        title_y = SCREEN_HEIGHT // 2 - scaled_height // 2 + self.title_y_offset
        
        # Dessiner l'ombre puis le titre
        self.screen.blit(shadow_surface, (title_x + shadow_offset, title_y + shadow_offset))
        self.screen.blit(title_alpha, (title_x, title_y))
        
        # Sous-titre avec effet de fade-in
        if self.timer > 1.0:
            subtitle_alpha = min(255, int((self.timer - 1.0) * 255))
            subtitle_text = "Plateformer 2D Compétitif"
            subtitle_surface = self.font_subtitle.render(subtitle_text, True, YELLOW)
            subtitle_alpha_surf = pygame.Surface(subtitle_surface.get_size(), pygame.SRCALPHA)
            subtitle_alpha_surf.fill((255, 255, 255, subtitle_alpha))
            subtitle_alpha_surf.blit(subtitle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            subtitle_x = SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2
            subtitle_y = title_y + scaled_height + 30
            self.screen.blit(subtitle_alpha_surf, (subtitle_x, subtitle_y))
        
        # Message "Appuyez pour continuer"
        if self.timer > 2.0:
            blink = int(self.timer * 2) % 2
            if blink:
                press_text = "Appuyez sur une touche pour continuer..."
                press_surface = self.font_press.render(press_text, True, WHITE)
                press_x = SCREEN_WIDTH // 2 - press_surface.get_width() // 2
                press_y = SCREEN_HEIGHT - 100
                self.screen.blit(press_surface, (press_x, press_y))
        
        # Effet de particules autour du titre (optionnel)
        if self.timer > 1.0:
            for i in range(8):
                angle = (self.timer * 50 + i * 45) * math.pi / 180
                radius = 100 + math.sin(self.timer * 2) * 20
                particle_x = SCREEN_WIDTH // 2 + math.cos(angle) * radius
                particle_y = SCREEN_HEIGHT // 2 + math.sin(angle) * radius
                particle_size = 3 + int(math.sin(self.timer * 3 + i) * 2)
                pygame.draw.circle(self.screen, CYAN, (int(particle_x), int(particle_y)), particle_size)
    
    def is_finished(self):
        """Vérifie si l'écran d'accueil est terminé"""
        return self.finished or self.timer > 5.0  # Auto-passer après 5 secondes

