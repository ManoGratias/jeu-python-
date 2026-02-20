"""
Gestionnaire de matchs - Gère les manches et le cycle Course → Récompenses → Combat
"""
import pygame
from config import *

class MatchManager:
    def __init__(self, game_mode="1v1", num_rounds=5):
        """
        game_mode: "1v1" (Joueur vs Bot), "2v1" (2 Joueurs vs Bot), "pvp" (Joueur vs Joueur)
        num_rounds: Nombre de manches (5 par défaut)
        """
        self.game_mode = game_mode
        self.num_rounds = num_rounds
        self.current_round = 0
        self.round_state = "race"  # "race", "rewards", "combat", "round_complete"
        
        # Scores des joueurs
        self.player1_score = 0
        self.player2_score = 0
        self.bot_score = 0
        
        # Victoires par manche
        self.player1_wins = 0
        self.player2_wins = 0
        self.bot_wins = 0
        
        # État actuel
        self.race_completed = False
        self.rewards_shown = False
        self.combat_completed = False
        self.match_lost = False  # True si le joueur a perdu (timeout boss)
        
        # Récompenses de la course actuelle
        self.current_rewards = {
            "player1": {"coins": 0, "items": []},
            "player2": {"coins": 0, "items": []} if game_mode in ["2v1", "pvp"] else None
        }
        
    def start_match(self):
        """Démarre un nouveau match (intro Manche 1 puis course)"""
        self.current_round = 1
        self.round_state = "round_intro"  # Affiche "MANCHE 1" avant la 1ère course
        self.player1_score = 0
        self.player2_score = 0
        self.bot_score = 0
        self.player1_wins = 0
        self.player2_wins = 0
        self.bot_wins = 0
    
    def load_state(self, current_round, player1_wins, bot_wins, match_complete=False):
        """Charge l'état d'un match en cours (après sauvegarde)"""
        self.player1_wins = player1_wins
        self.player2_wins = 0
        self.bot_wins = bot_wins
        self.player1_score = player1_wins
        self.player2_score = 0
        self.bot_score = bot_wins
        self.current_round = current_round
        if match_complete:
            self.round_state = "match_complete"
        else:
            self.round_state = "race"
        
    def complete_race(self, player1_time, player2_time=None, bot_time=None):
        """Marque la course comme terminée : 1 point au premier arrivé + récompenses"""
        self.race_completed = True
        self.round_state = "rewards"  # Affiche victoire, puis combat ou fin
        
        # 1 POINT pour le premier qui finit la course
        if self.game_mode == "pvp" and player2_time is not None:
            if player1_time < player2_time:
                self.player1_wins += 1
                self.player1_score += 1
                self.current_rewards["player1"]["coins"] = 100
                self.current_rewards["player2"]["coins"] = 50
            elif player2_time < player1_time:
                self.player2_wins += 1
                self.player2_score += 1
                self.current_rewards["player1"]["coins"] = 50
                self.current_rewards["player2"]["coins"] = 100
            else:
                self.current_rewards["player1"]["coins"] = 75
                self.current_rewards["player2"]["coins"] = 75
        elif self.game_mode == "2v1" and player2_time is not None:
            if player1_time <= player2_time:
                self.player1_wins += 1
                self.player1_score += 1
                self.current_rewards["player1"]["coins"] = 100
                self.current_rewards["player2"]["coins"] = 75
            else:
                self.player2_wins += 1
                self.player2_score += 1
                self.current_rewards["player1"]["coins"] = 75
                self.current_rewards["player2"]["coins"] = 100
        elif self.game_mode == "1v1" and bot_time is not None:
            if player1_time < bot_time:
                self.player1_wins += 1
                self.player1_score += 1
            else:
                self.bot_wins += 1
                self.bot_score += 1
            self.current_rewards["player1"]["coins"] = 100
        else:
            self.current_rewards["player1"]["coins"] = 100
        
        # Ajouter des items aléatoires
        self._generate_random_items()
        
    def _generate_random_items(self):
        """Génère des items aléatoires comme récompenses"""
        import random
        items = ["speed_boost", "shield", "double_jump", "slow_time"]
        # 30% de chance d'obtenir un item
        if random.random() < 0.3:
            self.current_rewards["player1"]["items"].append(random.choice(items))
        if self.current_rewards["player2"] and random.random() < 0.3:
            self.current_rewards["player2"]["items"].append(random.choice(items))
    
    def show_rewards(self):
        """Affiche les récompenses puis mini-jeu selon la manche"""
        self.rewards_shown = True
        # Manche 5 = pas de mini-jeu, match terminé
        if self.current_round == self.num_rounds:
            self.round_state = "match_complete"
        elif self.current_round == 1:
            # Manche 1 = Combat classique
            self.round_state = "combat"
        elif self.current_round == 2:
            # Manche 2 = Morpion
            self.round_state = "minigame_morpion"
        elif self.current_round == 3:
            # Manche 3 = Sol en Lave
            self.round_state = "minigame_lava"
        elif self.current_round == 4:
            # Manche 4 = Pas de mini-jeu, affiche les récompenses puis passe à la manche 5
            # On reste en "rewards" pour afficher les récompenses, puis on passera à round_intro
            self.round_state = "rewards"
        else:
            # Autres manches = combat classique
            self.round_state = "combat"
        
    def complete_combat(self, winner):
        """Marque le combat/mini-jeu comme terminé - 5 points pour le gagnant (None = égalité, pas de points)"""
        self.combat_completed = True
        
        # Enregistrer la victoire - 5 POINTS pour le gagnant (seulement si winner n'est pas None)
        if winner == "player1":
            self.player1_wins += 1
            self.player1_score += 5  # 5 points
        elif winner == "player2":
            self.player2_wins += 1
            self.player2_score += 5  # 5 points
        elif winner == "bot":
            self.bot_wins += 1
            self.bot_score += 5  # 5 points
        # Si winner est None (égalité), pas de points et pas de victoire enregistrée
        
        # Passer à la manche suivante ou terminer le match
        if self.current_round < self.num_rounds:
            self.current_round += 1
            self.round_state = "round_intro"  # Animation "Manche X" avant la course
            self.race_completed = False
            self.rewards_shown = False
            self.combat_completed = False
            self.current_rewards = {
                "player1": {"coins": 0, "items": []},
                "player2": {"coins": 0, "items": []} if self.game_mode in ["2v1", "pvp"] else None
            }
        else:
            self.round_state = "match_complete"
    
    def get_match_winner(self):
        """Retourne le gagnant du match"""
        if self.game_mode == "pvp":
            if self.player1_wins > self.player2_wins:
                return "player1"
            elif self.player2_wins > self.player1_wins:
                return "player2"
            else:
                return "tie"
        elif self.game_mode == "1v1":
            if self.player1_wins > self.bot_wins:
                return "player1"
            elif self.bot_wins > self.player1_wins:
                return "bot"
            else:
                return "tie"
        else:  # 2v1
            combined_wins = self.player1_wins + self.player2_wins
            if combined_wins > self.bot_wins:
                return "players"
            elif self.bot_wins > combined_wins:
                return "bot"
            else:
                return "tie"
    
    def is_match_complete(self):
        """Vérifie si le match est terminé"""
        return self.round_state == "match_complete"
    
    def get_round_info(self):
        """Retourne les informations de la manche actuelle"""
        return {
            "round": self.current_round,
            "total_rounds": self.num_rounds,
            "state": self.round_state,
            "player1_wins": self.player1_wins,
            "player2_wins": self.player2_wins,
            "bot_wins": self.bot_wins
        }

