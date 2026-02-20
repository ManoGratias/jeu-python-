"""
Système de Morpion (Tic-Tac-Toe) - Mini-jeu après manche 2
Le gagnant remporte 5 points
"""
import pygame
import random
from config import *

class TicTacToeSystem:
    def __init__(self, match_manager):
        self.match_manager = match_manager
        self.game_active = False
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]  # Grille 3x3
        self.current_player = 'X'  # X = Joueur 1, O = Joueur 2/Bot
        self.winner = None
        self.game_over = False
        self.cell_size = 120
        self.board_x = SCREEN_WIDTH // 2 - (self.cell_size * 3) // 2
        self.board_y = SCREEN_HEIGHT // 2 - (self.cell_size * 3) // 2 - 50
        
    def start_game(self):
        """Démarre une nouvelle partie de Morpion - Joueur commence"""
        self.game_active = True
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.current_player = 'X'  # Joueur commence (X)
        self.winner = None
        self.game_over = False
        self.player1_moves = 0  # Compteur de coups joueur 1 (max 3)
        self.player2_moves = 0  # Compteur de coups joueur 2/bot (max 3)
        self.selected_row = 0  # Initialiser la sélection
        self.selected_col = 0
        
    def make_move(self, row, col, player_symbol):
        """Fait un mouvement sur la grille"""
        if self.game_over or self.board[row][col] != '':
            return False
        
        self.board[row][col] = player_symbol
        # Compter les coups par joueur (max 3 chacun)
        if player_symbol == 'X':
            self.player1_moves += 1
        else:  # 'O'
            self.player2_moves += 1
        
        self._check_winner()
        
        if not self.game_over:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            # Limite : 3 coups max par joueur
            if self.player1_moves >= 3 and self.player2_moves >= 3:
                self.game_over = True
                self.winner = 'tie'
        
        return True
    
    def _check_winner(self):
        """Vérifie s'il y a un gagnant"""
        # Vérifier les lignes
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                self.winner = row[0]
                self.game_over = True
                return
        
        # Vérifier les colonnes
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                self.winner = self.board[0][col]
                self.game_over = True
                return
        
        # Vérifier les diagonales
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            self.winner = self.board[0][0]
            self.game_over = True
            return
        
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            self.winner = self.board[0][2]
            self.game_over = True
            return
        
        # Vérifier égalité (grille pleine OU 3 coups chacun joués)
        if all(self.board[i][j] != '' for i in range(3) for j in range(3)) or (self.player1_moves >= 3 and self.player2_moves >= 3):
            if self.winner is None:  # Pas de gagnant = égalité
                self.game_over = True
                self.winner = 'tie'
    
    def bot_move(self):
        """IA simple pour le bot - MAX 3 COUPS"""
        if self.game_over or self.current_player != 'O' or self.player2_moves >= 3:
            return
        
        # Essayer de gagner
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    self.board[i][j] = 'O'
                    self._check_winner()
                    if self.winner == 'O':
                        self.player2_moves += 1
                        self.current_player = 'X'
                        return
                    self.board[i][j] = ''
        
        # Bloquer le joueur
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    self.board[i][j] = 'X'
                    self._check_winner()
                    if self.winner == 'X':
                        self.board[i][j] = 'O'
                        self.winner = None
                        self.game_over = False
                        self.player2_moves += 1
                        self.current_player = 'X'
                        return
                    self.board[i][j] = ''
        
        # Coup aléatoire (seulement si moins de 3 coups)
        if self.player2_moves < 3:
            available = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == '']
            if available:
                row, col = random.choice(available)
                self.make_move(row, col, 'O')
    
    def get_winner_for_match(self):
        """Retourne le gagnant pour le match_manager - égalité = None (pas de points)"""
        if self.winner == 'X':
            return 'player1'
        elif self.winner == 'O':
            if self.match_manager.game_mode == "pvp":
                return 'player2'
            else:
                return 'bot'
        elif self.winner == 'tie':
            return None  # Égalité = pas de points
        return None
    
    def handle_click(self, mouse_pos):
        """Gère un clic de souris sur la grille"""
        if self.game_over or self.current_player != 'X':
            return False
        
        x, y = mouse_pos
        col = (x - self.board_x) // self.cell_size
        row = (y - self.board_y) // self.cell_size
        
        if 0 <= row < 3 and 0 <= col < 3:
            return self.make_move(row, col, 'X')
        return False
    
    def handle_controller_selection(self, direction):
        """Gère la sélection avec la manette (direction = 'up', 'down', 'left', 'right', 'select')"""
        if self.game_over or self.current_player != 'X':
            return False
        
        # Initialiser la sélection si nécessaire
        if not hasattr(self, 'selected_row') or not hasattr(self, 'selected_col'):
            self.selected_row = 0
            self.selected_col = 0
        
        if direction == 'up' and self.selected_row > 0:
            self.selected_row -= 1
            return True  # Indiquer qu'on a bougé
        elif direction == 'down' and self.selected_row < 2:
            self.selected_row += 1
            return True
        elif direction == 'left' and self.selected_col > 0:
            self.selected_col -= 1
            return True
        elif direction == 'right' and self.selected_col < 2:
            self.selected_col += 1
            return True
        elif direction == 'select':
            # Vérifier que la case est vide avant de jouer
            if self.board[self.selected_row][self.selected_col] == '':
                return self.make_move(self.selected_row, self.selected_col, 'X')
        
        return False
    
    def get_selected_cell_pos(self):
        """Retourne la position de la case sélectionnée pour l'affichage"""
        if hasattr(self, 'selected_row') and hasattr(self, 'selected_col'):
            x = self.board_x + self.selected_col * self.cell_size
            y = self.board_y + self.selected_row * self.cell_size
            return (x, y)
        return None
    
    def draw(self, screen):
        """Dessine le jeu de Morpion"""
        if not self.game_active:
            return
        
        # Fond
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Titre
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("🎮 MORPION 🎮", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        subtitle = pygame.font.Font(None, 28).render("5 points pour le gagnant!", True, CYAN)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 100))
        
        # Instructions détaillées
        font_small = pygame.font.Font(None, 24)
        font_tiny = pygame.font.Font(None, 20)
        
        if self.match_manager.game_mode == "pvp":
            if self.current_player == 'X':
                player_text = "Joueur 1 (X) - Votre tour!"
            else:
                player_text = "Joueur 2 (O) - Votre tour!"
        else:
            if self.current_player == 'X':
                player_text = "Votre tour (X) - Jouez maintenant!"
            else:
                player_text = "Tour du Bot (O)..."
        
        player_inst = font_small.render(player_text, True, YELLOW if self.current_player == 'X' else CYAN)
        screen.blit(player_inst, (SCREEN_WIDTH // 2 - player_inst.get_width() // 2, 130))
        
        # Afficher le nombre de coups restants
        if self.match_manager.game_mode == "pvp":
            moves_info = f"J1: {3 - self.player1_moves} coups restants | J2: {3 - self.player2_moves} coups restants"
        else:
            moves_info = f"Vous: {3 - self.player1_moves} coups restants | Bot: {3 - self.player2_moves} coups restants"
        moves_text = font_small.render(moves_info, True, WHITE)
        screen.blit(moves_text, (SCREEN_WIDTH // 2 - moves_text.get_width() // 2, 160))
        
        # Contrôles
        controls = [
            "CLAVIER: Flèches ←→↑↓ pour naviguer | ESPACE/ENTRÉE pour placer",
            "MANETTE: D-Pad/Stick pour naviguer | Bouton X pour placer",
            "SOURIS: Cliquez directement sur une case vide"
        ]
        
        y_pos = 160
        for ctrl in controls:
            ctrl_text = font_tiny.render(ctrl, True, WHITE)
            screen.blit(ctrl_text, (SCREEN_WIDTH // 2 - ctrl_text.get_width() // 2, y_pos))
            y_pos += 22
        
        # Objectif
        goal_text = font_tiny.render("🎯 Objectif: Aligner 3 symboles (ligne, colonne ou diagonale) pour gagner!", True, GREEN)
        screen.blit(goal_text, (SCREEN_WIDTH // 2 - goal_text.get_width() // 2, y_pos + 5))
        
        # Dessiner la grille
        for i in range(3):
            for j in range(3):
                x = self.board_x + j * self.cell_size
                y = self.board_y + i * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                # Fond de la case (surbrillance si sélectionnée)
                selected_pos = self.get_selected_cell_pos()
                if selected_pos and abs(x - selected_pos[0]) < 5 and abs(y - selected_pos[1]) < 5:
                    pygame.draw.rect(screen, CYAN, rect)
                    pygame.draw.rect(screen, WHITE, rect, 4)
                else:
                    pygame.draw.rect(screen, DARK_GRAY, rect)
                    pygame.draw.rect(screen, WHITE, rect, 3)
                
                # Symbole
                if self.board[i][j] == 'X':
                    # Dessiner X (rouge)
                    pygame.draw.line(screen, RED, (x + 15, y + 15), (x + self.cell_size - 15, y + self.cell_size - 15), 8)
                    pygame.draw.line(screen, RED, (x + self.cell_size - 15, y + 15), (x + 15, y + self.cell_size - 15), 8)
                elif self.board[i][j] == 'O':
                    # Dessiner O (bleu)
                    pygame.draw.circle(screen, BLUE, (x + self.cell_size // 2, y + self.cell_size // 2), self.cell_size // 2 - 15, 8)
        
        # Message de fin
        if self.game_over:
            font_medium = pygame.font.Font(None, 48)
            if self.winner == 'X':
                msg = "Joueur 1 gagne! +5 points"
                color = RED
            elif self.winner == 'O':
                if self.match_manager.game_mode == "pvp":
                    msg = "Joueur 2 gagne! +5 points"
                else:
                    msg = "Bot gagne! +5 points"
                color = BLUE
            else:
                msg = "Égalité!"
                color = GRAY
            
            msg_text = font_medium.render(msg, True, color)
            screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 100))
            
            hint = font_small.render("Appuyez sur ESPACE ou X pour continuer", True, WHITE)
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 60))

