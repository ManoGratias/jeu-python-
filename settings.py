"""
Gestion des paramètres du jeu avec sauvegarde
"""
import json
import os

SETTINGS_FILE = "settings.json"

class Settings:
    def __init__(self):
        self.joystick_enabled = True  # Par défaut activé si manette détectée
        self.load_settings()
    
    def load_settings(self):
        """Charge les paramètres depuis le fichier JSON"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.joystick_enabled = data.get("joystick_enabled", True)
            except (json.JSONDecodeError, IOError):
                self.joystick_enabled = True
        else:
            self.joystick_enabled = True
    
    def save_settings(self):
        """Sauvegarde les paramètres dans le fichier JSON"""
        try:
            data = {
                "joystick_enabled": self.joystick_enabled
            }
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError:
            print("Erreur lors de la sauvegarde des paramètres")
    
    def toggle_joystick(self):
        """Active/désactive la manette"""
        self.joystick_enabled = not self.joystick_enabled
        self.save_settings()

