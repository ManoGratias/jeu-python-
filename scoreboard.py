"""
Gestion du scoreboard avec sauvegarde JSON
"""
import json
import os
from datetime import datetime
from config import SCORES_FILE

class Scoreboard:
    def __init__(self):
        self.scores = []
        self.load_scores()
    
    def load_scores(self):
        """Charge les scores depuis le fichier JSON"""
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.scores = []
        else:
            self.scores = []
    
    def save_scores(self):
        """Sauvegarde les scores dans le fichier JSON"""
        try:
            with open(SCORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except IOError:
            print("Erreur lors de la sauvegarde des scores")
    
    def add_score(self, pseudo, score):
        """Ajoute un nouveau score"""
        score_entry = {
            "pseudo": pseudo,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.scores.append(score_entry)
        # Trier par score décroissant
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        # Garder seulement le top 10
        self.scores = self.scores[:10]
        self.save_scores()
    
    def get_top_10(self):
        """Retourne le top 10 des scores"""
        return self.scores[:10]
    
    def get_rank(self, score):
        """Retourne le rang d'un score (1-indexed)"""
        rank = 1
        for entry in self.scores:
            if score > entry["score"]:
                return rank
            rank += 1
        return rank if rank <= 10 else None

