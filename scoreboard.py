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
        # Charger TOUS les scores existants (conserve tous les scores en mémoire)
        self.load_scores()
    
    def clear_scores(self):
        """Vide le scoreboard (supprime le fichier)"""
        if os.path.exists(SCORES_FILE):
            try:
                os.remove(SCORES_FILE)
                print(f"[DEBUG] Scoreboard vidé - nouveau système activé")
            except IOError:
                print(f"[DEBUG] Erreur lors de la suppression du scoreboard")
    
    def load_scores(self):
        """Charge TOUS les scores depuis le fichier JSON (conserve tous les scores en mémoire)"""
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                # Charger TOUS les scores (pas de dédoublonnage, pas de limite)
                self.scores = []
                for entry in raw:
                    pseudo = entry.get("pseudo", "").strip()
                    if not pseudo:
                        continue
                    date = entry.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    score = entry.get("score", 0)
                    boss_time = entry.get("boss_time", None)  # Temps pour battre le boss (en secondes)
                    
                    self.scores.append({
                        "pseudo": pseudo,
                        "score": score,
                        "boss_time": boss_time,
                        "date": date
                    })
                
                # Trier : d'abord par score décroissant, puis par temps croissant (meilleur temps = mieux)
                self.scores.sort(key=lambda x: (-x["score"], x.get("boss_time", float('inf'))))
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
    
    def add_score(self, pseudo, score, boss_time=None):
        """Ajoute un nouveau score (conserve TOUS les scores en mémoire)
        
        Args:
            pseudo: Le pseudo du joueur
            score: Le score total (points)
            boss_time: Le temps pris pour battre le boss en secondes (optionnel)
        """
        pseudo_clean = pseudo.strip()
        if not pseudo_clean:
            return
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ajouter le nouveau score (TOUS les scores sont conservés)
        self.scores.append({
            "pseudo": pseudo_clean,
            "score": score,
            "boss_time": boss_time,
            "date": now
        })
        
        # Trier : d'abord par score décroissant, puis par temps croissant (meilleur temps = mieux)
        self.scores.sort(key=lambda x: (-x["score"], x.get("boss_time", float('inf'))))
        # Sauvegarder TOUS les scores (pas de limite)
        self.save_scores()
    
    def get_top_10(self):
        """Retourne le top 10 des scores"""
        return self.scores[:10]
    
    def get_rank(self, score, boss_time=None):
        """Retourne le rang d'un score (1-indexed) - calcule parmi TOUS les scores
        
        Args:
            score: Le score total (points)
            boss_time: Le temps pris pour battre le boss en secondes (optionnel)
        """
        rank = 1
        for entry in self.scores:
            entry_score = entry["score"]
            entry_time = entry.get("boss_time")
            
            # Comparer : meilleur score OU même score mais meilleur temps
            if score > entry_score:
                return rank
            elif score == entry_score:
                if boss_time is not None and entry_time is not None:
                    if boss_time < entry_time:
                        return rank
                elif boss_time is not None and entry_time is None:
                    return rank  # Un temps est meilleur qu'aucun temps
            rank += 1
        return rank  # Retourne le rang même s'il dépasse 10

