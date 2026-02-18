"""
Système d'objets et sorts stratégiques
"""
import pygame
from config import *

class ItemsSystem:
    def __init__(self):
        self.items = {
            "speed_boost": {
                "name": "Boost de vitesse",
                "icon": "⚡",
                "description": "Augmente la vitesse de déplacement",
                "duration": 10,  # secondes
                "effect": "speed_multiplier",
                "value": 1.5
            },
            "shield": {
                "name": "Bouclier",
                "icon": "🛡️",
                "description": "Réduit les dégâts reçus",
                "duration": 0,  # Permanent jusqu'à la fin du combat
                "effect": "damage_reduction",
                "value": 0.5  # Réduit les dégâts de 50%
            },
            "double_jump": {
                "name": "Double saut",
                "icon": "🦘",
                "description": "Permet un saut supplémentaire",
                "duration": 0,  # Permanent pour la course
                "effect": "extra_jump",
                "value": 1
            },
            "slow_time": {
                "name": "Ralentissement",
                "icon": "⏱️",
                "description": "Ralentit les ennemis",
                "duration": 5,
                "effect": "enemy_slow",
                "value": 0.5  # Réduit la vitesse des ennemis de 50%
            }
        }
        
        # Items actifs par joueur
        self.active_items = {
            "player1": {},
            "player2": {}
        }
        
        # Timers pour les items temporaires
        self.item_timers = {
            "player1": {},
            "player2": {}
        }
    
    def activate_item(self, player_id, item_name):
        """Active un item pour un joueur"""
        if item_name not in self.items:
            return False
        
        item = self.items[item_name]
        
        # Ajouter l'item aux actifs
        self.active_items[player_id][item_name] = {
            "effect": item["effect"],
            "value": item["value"],
            "start_time": pygame.time.get_ticks() / 1000  # Temps en secondes
        }
        
        # Si l'item a une durée, ajouter un timer
        if item["duration"] > 0:
            self.item_timers[player_id][item_name] = item["duration"]
        
        return True
    
    def update(self):
        """Met à jour les timers des items"""
        current_time = pygame.time.get_ticks() / 1000
        
        for player_id in ["player1", "player2"]:
            items_to_remove = []
            
            for item_name, item_data in self.active_items[player_id].items():
                item_info = self.items[item_name]
                
                # Vérifier si l'item a expiré
                if item_info["duration"] > 0:
                    elapsed = current_time - item_data["start_time"]
                    if elapsed >= item_info["duration"]:
                        items_to_remove.append(item_name)
            
            # Retirer les items expirés
            for item_name in items_to_remove:
                del self.active_items[player_id][item_name]
                if item_name in self.item_timers[player_id]:
                    del self.item_timers[player_id][item_name]
    
    def has_item(self, player_id, item_name):
        """Vérifie si un joueur a un item actif"""
        return item_name in self.active_items[player_id]
    
    def get_item_effect(self, player_id, item_name):
        """Récupère l'effet d'un item"""
        if item_name in self.active_items[player_id]:
            return self.active_items[player_id][item_name]
        return None
    
    def get_speed_multiplier(self, player_id):
        """Récupère le multiplicateur de vitesse"""
        if self.has_item(player_id, "speed_boost"):
            return self.items["speed_boost"]["value"]
        return 1.0
    
    def get_damage_reduction(self, player_id):
        """Récupère la réduction de dégâts"""
        if self.has_item(player_id, "shield"):
            return self.items["shield"]["value"]
        return 1.0  # Pas de réduction
    
    def clear_items(self, player_id):
        """Efface tous les items d'un joueur"""
        self.active_items[player_id] = {}
        self.item_timers[player_id] = {}
    
    def draw_active_items(self, screen, player_id, x, y):
        """Dessine les items actifs d'un joueur"""
        if not self.active_items[player_id]:
            return
        
        font = pygame.font.Font(None, 20)
        y_offset = 0
        
        for item_name in self.active_items[player_id]:
            item = self.items[item_name]
            item_text = f"{item['icon']} {item['name']}"
            
            # Si l'item a une durée, afficher le temps restant
            if item["duration"] > 0:
                elapsed = (pygame.time.get_ticks() / 1000) - self.active_items[player_id][item_name]["start_time"]
                remaining = max(0, item["duration"] - elapsed)
                item_text += f" ({int(remaining)}s)"
            
            text = font.render(item_text, True, GREEN)
            screen.blit(text, (x, y + y_offset))
            y_offset += 25

