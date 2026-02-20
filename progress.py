"""
Sauvegarde et chargement de la progression du jeu
Un niveau est considéré terminé après le combat
"""
import json
import os

PROGRESS_FILE = "progress.json"


def save_progress(data):
    """Sauvegarde la progression dans un fichier JSON"""
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde progression: {e}")
        return False


def load_progress():
    """Charge la progression depuis le fichier JSON"""
    if not os.path.exists(PROGRESS_FILE):
        return None
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur chargement progression: {e}")
        return None


def get_joueur_vs_bot_progress():
    """Récupère la progression Joueur vs Bot"""
    data = load_progress()
    if data and "joueur_vs_bot" in data:
        return data["joueur_vs_bot"]
    return None


def save_joueur_vs_bot_progress(current_round, num_rounds, player1_wins, bot_wins, match_complete=False):
    """Sauvegarde la progression Joueur vs Bot (après chaque combat)"""
    data = load_progress() or {}
    data["joueur_vs_bot"] = {
        "current_round": current_round,
        "num_rounds": num_rounds,
        "player1_wins": player1_wins,
        "bot_wins": bot_wins,
        "match_complete": match_complete
    }
    return save_progress(data)


def reset_joueur_vs_bot_progress():
    """Réinitialise la progression Joueur vs Bot"""
    data = load_progress() or {}
    if "joueur_vs_bot" in data:
        del data["joueur_vs_bot"]
    return save_progress(data)

