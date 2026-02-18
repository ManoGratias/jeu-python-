"""
Menu des paramètres
"""
import pygame
from config import *

class SettingsMenu:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.selected_option = 0
        self.options = ["Manette PS4", "Retour"]
        self.font_title = pygame.font.Font(None, 72)
        self.font_option = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
    
    def handle_event(self, event):
        """Gère les événements du menu paramètres"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_option == 0:  # Manette PS4
                    self.settings.toggle_joystick()
                elif self.selected_option == 1:  # Retour
                    return "retour"
            elif event.key == pygame.K_ESCAPE:
                return "retour"
        return None
    
    def handle_joystick_event(self, event):
        """Gère les événements de manette dans le menu paramètres"""
        try:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Bouton X
                    if self.selected_option == 0:  # Manette PS4
                        self.settings.toggle_joystick()
                    elif self.selected_option == 1:  # Retour
                        return "retour"
                elif event.button == 9:  # Bouton Options
                    return "retour"
            
            elif event.type == pygame.JOYHATMOTION:
                if hasattr(event, 'joy') and event.joy < pygame.joystick.get_count():
                    hat = pygame.joystick.Joystick(event.joy).get_hat(0)
                    if hat[1] == 1:  # Haut
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif hat[1] == -1:  # Bas
                        self.selected_option = (self.selected_option + 1) % len(self.options)
        except (AttributeError, IndexError, KeyError):
            pass  # Ignorer les erreurs de manette
        
        return None
    
    def draw(self):
        """Dessine le menu paramètres"""
        self.screen.fill(BLACK)
        
        # Titre
        title = self.font_title.render("PARAMÈTRES", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Options du menu
        y_offset = 350
        for i, option in enumerate(self.options):
            color = CYAN if i == self.selected_option else WHITE
            
            # Texte de l'option
            if i == 0:  # Manette PS4
                status = "Activée" if self.settings.joystick_enabled else "Désactivée"
                status_color = GREEN if self.settings.joystick_enabled else RED
                text = self.font_option.render(f"{option}: {status}", True, color)
            else:
                text = self.font_option.render(option, True, color)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 80))
            self.screen.blit(text, text_rect)
            
            # Indicateur de sélection
            if i == self.selected_option:
                pygame.draw.polygon(self.screen, CYAN, [
                    (text_rect.left - 30, text_rect.centery),
                    (text_rect.left - 10, text_rect.centery - 10),
                    (text_rect.left - 10, text_rect.centery + 10)
                ])
            
            # Afficher le statut de la manette avec couleur
            if i == 0:
                status_text = self.font_small.render(
                    "Activée" if self.settings.joystick_enabled else "Désactivée",
                    True, GREEN if self.settings.joystick_enabled else RED
                )
                status_rect = status_text.get_rect(center=(SCREEN_WIDTH // 2 + 200, y_offset + i * 80))
                self.screen.blit(status_text, status_rect)
        
        # Instructions
        instructions = [
            "Flèches ↑↓ : Naviguer | Entrée/Espace : Activer/Désactiver",
            "ESC : Retour"
        ]
        y_inst = SCREEN_HEIGHT - 100
        for i, inst in enumerate(instructions):
            text = self.font_small.render(inst, True, GRAY)
            self.screen.blit(text, (50, y_inst + i * 30))

