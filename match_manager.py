"""
Gestionnaire de matchs - Gère les manches et le cycle Course → Récompenses → Combat
"""
import pygame
from config import *

class MatchManager:
    def __init__(self, game_mode="1v1", num_rounds=10):
        """
        game_mode: "1v1" (Joueur vs Bot), "2v1" (2 Joueurs vs Bot), "pvp" (Joueur vs Joueur)
        num_rounds: Nombre de manches (5 ou 10)
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
        
        # Récompenses de la course actuelle
        self.current_rewards = {
            "player1": {"coins": 0, "items": []},
            "player2": {"coins": 0, "items": []} if game_mode in ["2v1", "pvp"] else None
        }
        
    def start_match(self):
        """Démarre un nouveau match"""
        self.current_round = 1
        self.round_state = "race"
        self.player1_score = 0
        self.player2_score = 0
        self.bot_score = 0
        self.player1_wins = 0
        self.player2_wins = 0
        self.bot_wins = 0
        
    def complete_race(self, player1_time, player2_time=None):
        """Marque la course comme terminée et calcule les récompenses"""
        self.race_completed = True
        self.round_state = "rewards"
        
        # Calculer les récompenses basées sur le temps
        # Le joueur le plus rapide gagne plus de pièces
        if self.game_mode == "pvp":
            if player1_time < player2_time:
                self.current_rewards["player1"]["coins"] = 100
                self.current_rewards["player2"]["coins"] = 50
            elif player2_time < player1_time:
                self.current_rewards["player1"]["coins"] = 50
                self.current_rewards["player2"]["coins"] = 100
            else:
                self.current_rewards["player1"]["coins"] = 75
                self.current_rewards["player2"]["coins"] = 75
        else:
            # Mode 1v1 ou 2v1
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
        """Affiche les récompenses et passe au combat"""
        self.rewards_shown = True
        self.round_state = "combat"
        
    def complete_combat(self, winner):
        """Marque le combat comme terminé"""
        self.combat_completed = True
        
        # Enregistrer la victoire
        if winner == "player1":
            self.player1_wins += 1
            self.player1_score += 1
        elif winner == "player2":
            self.player2_wins += 1
            self.player2_score += 1
        elif winner == "bot":
            self.bot_wins += 1
            self.bot_score += 1
        
        # Passer à la manche suivante ou terminer le match
        if self.current_round < self.num_rounds:
            self.current_round += 1
            self.round_state = "race"
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

