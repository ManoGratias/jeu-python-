"""
IA pour les bots dans les différents modes
"""
import random
import pygame
from config import *

class BotAI:
    def __init__(self, difficulty="medium"):
        """
        difficulty: "easy", "medium", "hard"
        """
        self.difficulty = difficulty
        
        # Paramètres selon la difficulté
        self.difficulty_params = {
            "easy": {
                "race_speed_multiplier": 0.7,  # 70% de la vitesse normale
                "combat_attack_chance": 0.01,  # 1% par frame
                "combat_damage": 10,
                "reaction_time": 0.3  # secondes
            },
            "medium": {
                "race_speed_multiplier": 0.9,  # 90% de la vitesse normale
                "combat_attack_chance": 0.02,  # 2% par frame
                "combat_damage": 15,
                "reaction_time": 0.15
            },
            "hard": {
                "race_speed_multiplier": 1.1,  # 110% de la vitesse normale
                "combat_attack_chance": 0.03,  # 3% par frame
                "combat_damage": 20,
                "reaction_time": 0.05
            }
        }
        
        self.params = self.difficulty_params[difficulty]
        
    def get_race_speed(self, base_speed):
        """Retourne la vitesse du bot pour la course"""
        return base_speed * self.params["race_speed_multiplier"]
    
    def should_attack(self):
        """Détermine si le bot doit attaquer"""
        return random.random() < self.params["combat_attack_chance"]
    
    def get_combat_damage(self):
        """Retourne les dégâts du bot"""
        return self.params["combat_damage"]
    
    def get_reaction_time(self):
        """Retourne le temps de réaction du bot"""
        return self.params["reaction_time"]
    
    def simulate_race_time(self, player_time):
        """Simule le temps de course du bot basé sur le temps du joueur"""
        # Le bot finit généralement entre 80% et 120% du temps du joueur selon la difficulté
        if self.difficulty == "easy":
            multiplier = random.uniform(1.1, 1.4)  # Plus lent
        elif self.difficulty == "medium":
            multiplier = random.uniform(0.9, 1.2)  # Proche du joueur
        else:  # hard
            multiplier = random.uniform(0.7, 1.0)  # Plus rapide
        
        return player_time * multiplier

