"""
Écran de sélection des joueurs - Choisir qui contrôle le Joueur 1 et le Joueur 2
Avec 2 manettes : chaque joueur appuie sur X (J1) ou Cercle (J2) pour choisir.
"""
import pygame
from config import *

# Valeurs spéciales : -1 = pas encore choisi, None = clavier, 0/1 = manette
UNASSIGNED = -1

class PlayerSelection:
    """Permet à chaque joueur de choisir s'il est Joueur 1 ou Joueur 2"""
    
    def __init__(self, screen, num_joysticks):
        self.screen = screen
        self.num_joysticks = num_joysticks
        self.player1_joy_id = UNASSIGNED   # -1, None (clavier), 0, ou 1
        self.player2_joy_id = UNASSIGNED
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
    
    def handle_event(self, event):
        """
        Retourne "ready" quand les deux joueurs sont assignés,
        "back" si ESC, None sinon
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            if event.key == pygame.K_SPACE:
                self._assign_player1(None)  # J1 = Clavier
                return self._check_ready()
            if event.key == pygame.K_RETURN:
                self._assign_player2(None)  # J2 = Clavier
                return self._check_ready()
            if event.key == pygame.K_p:  # P = Passer (J1=M1, J2=M2 ou clavier)
                if self.num_joysticks >= 2:
                    self.player1_joy_id = 0
                    self.player2_joy_id = 1
                    return "ready"
                elif self.num_joysticks == 1:
                    self.player1_joy_id = 0
                    self.player2_joy_id = None
                    return "ready"
                else:
                    self.player1_joy_id = None
                    self.player2_joy_id = None
                    return "ready"
        
        if event.type == pygame.JOYBUTTONDOWN:
            joy_id = event.joy
            if joy_id >= self.num_joysticks:
                return None
            if event.button == 9:  # Bouton Options = Passer (défaut)
                if self.num_joysticks >= 2:
                    self.player1_joy_id = 0
                    self.player2_joy_id = 1
                    return "ready"
                elif self.num_joysticks == 1:
                    self.player1_joy_id = 0
                    self.player2_joy_id = None
                    return "ready"
            # X ou Cercle : ordre d'appui = premier = J1, deuxième = J2
            if event.button in (0, 1):  # X ou Cercle
                if self.player1_joy_id == UNASSIGNED:
                    self.player1_joy_id = joy_id
                elif self.player2_joy_id == UNASSIGNED and joy_id != self.player1_joy_id:
                    self.player2_joy_id = joy_id
                elif joy_id == self.player1_joy_id:
                    pass  # Déjà J1, ignorer
                elif joy_id == self.player2_joy_id:
                    pass  # Déjà J2, ignorer
                else:
                    # Cette manette n'est pas assignée : prendre le slot libre
                    if self.player2_joy_id == UNASSIGNED:
                        self.player2_joy_id = joy_id
                return self._check_ready()
        
        return None
    
    def _assign_player1(self, joy_id):
        """Assigne l'entrée pour le Joueur 1"""
        if self.player2_joy_id == joy_id and joy_id is not None:
            self.player2_joy_id = UNASSIGNED
        self.player1_joy_id = joy_id
    
    def _assign_player2(self, joy_id):
        """Assigne l'entrée pour le Joueur 2"""
        if self.player1_joy_id == joy_id and joy_id is not None:
            self.player1_joy_id = UNASSIGNED
        self.player2_joy_id = joy_id
    
    def _check_ready(self):
        """Vérifie si les deux joueurs ont une entrée assignée"""
        if self.player1_joy_id != UNASSIGNED and self.player2_joy_id != UNASSIGNED:
            return "ready"
        return None
    
    def is_ready(self):
        """Les deux joueurs ont-ils choisi leur entrée ?"""
        return (self.player1_joy_id != UNASSIGNED and 
                self.player2_joy_id != UNASSIGNED)
    
    def draw(self):
        """Dessine l'écran de sélection"""
        from config import GRADIENT_START, GRADIENT_END
        # Fond dégradé
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            self.screen.fill((r, g, b), (0, y, SCREEN_WIDTH, 1))
        
        # Titre
        title = self.font_large.render("CHOISISSEZ VOTRE JOUEUR", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        
        if self.num_joysticks >= 2:
            sub0 = self.font_small.render("2 manettes détectées ! Chacun appuie sur X ou Cercle avec SA manette.", True, YELLOW)
            self.screen.blit(sub0, (SCREEN_WIDTH // 2 - sub0.get_width() // 2, 115))
        sub1 = self.font_small.render("1er appui = J1  |  2ème appui = J2  |  Clavier : Espace = J1, Entrée = J2", True, GRAY)
        sub2 = self.font_small.render("P ou Options = Passer (J1=M1, J2=M2 si 2 manettes)", True, GRAY)
        self.screen.blit(sub1, (SCREEN_WIDTH // 2 - sub1.get_width() // 2, 140))
        self.screen.blit(sub2, (SCREEN_WIDTH // 2 - sub2.get_width() // 2, 165))
        
        # Panneaux Joueur 1 et Joueur 2
        half = SCREEN_WIDTH // 2
        self._draw_player_panel(half // 2, 220, "JOUEUR 1", self.player1_joy_id, BLUE)
        self._draw_player_panel(half + half // 2, 220, "JOUEUR 2", self.player2_joy_id, GREEN)
        
        # Instructions
        inst = self.font_small.render("ESC : Retour au menu", True, GRAY)
        self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, SCREEN_HEIGHT - 80))
        
        if self.is_ready():
            ready_text = self.font_medium.render("Prêt ! Démarrage automatique...", True, GREEN)
            self.screen.blit(ready_text, (SCREEN_WIDTH // 2 - ready_text.get_width() // 2, SCREEN_HEIGHT - 120))
    
    def _draw_player_panel(self, x, y, label, joy_id, color):
        """Dessine un panneau pour un joueur"""
        w, h = 280, 180
        rect = pygame.Rect(x - w // 2, y, w, h)
        pygame.draw.rect(self.screen, DARK_GRAY, rect)
        pygame.draw.rect(self.screen, color, rect, 3)
        
        title = self.font_medium.render(label, True, color)
        self.screen.blit(title, (x - title.get_width() // 2, y + 20))
        
        if joy_id == UNASSIGNED:
            status = "En attente..."
            status_color = GRAY
        elif joy_id is None:
            status = "Clavier"
            status_color = WHITE
        else:
            status = f"Manette {joy_id + 1}"
            status_color = YELLOW
        
        status_text = self.font_small.render(status, True, status_color)
        self.screen.blit(status_text, (x - status_text.get_width() // 2, y + 80))
