"""
Gestionnaire de sons pour Cyber Jump
Génère des sons synthétiques avec pygame.mixer
"""
import pygame
import math
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class SoundManager:
    def __init__(self):
        """Initialise le gestionnaire de sons"""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sound_enabled = True
        self.volume = 0.5  # Volume par défaut (0.0 à 1.0)
        
        # Créer tous les sons
        self._create_sounds()
    
    def _make_sound_array(self, frames):
        """Crée un array pour les sons"""
        if HAS_NUMPY:
            return np.zeros((frames, 2), dtype=np.int16)
        else:
            return [[0, 0] for _ in range(frames)]
    
    def _set_array_value(self, arr, i, value):
        """Définit une valeur dans l'array"""
        if HAS_NUMPY:
            arr[i][0] = value
            arr[i][1] = value
        else:
            arr[i] = [value, value]
    
    def _make_sound(self, arr):
        """Convertit un array en son pygame"""
        if HAS_NUMPY:
            return pygame.sndarray.make_sound(arr)
        else:
            # Sans numpy, créer un son directement avec pygame.mixer.Sound
            import array
            sound_data = array.array('h')
            for sample in arr:
                if isinstance(sample, list):
                    sound_data.append(sample[0])
                    sound_data.append(sample[1])
                else:
                    sound_data.append(sample[0])
                    sound_data.append(sample[1])
            # Créer un Sound directement avec les données brutes
            sound = pygame.mixer.Sound(buffer=bytes(sound_data))
            return sound
    
    def _create_sounds(self):
        """Crée tous les sons synthétiques"""
        self.sound_jump = self._create_jump_sound()
        self.sound_enemy_kill = self._create_enemy_kill_sound()
        self.sound_collectible = self._create_collectible_sound()
        self.sound_victory = self._create_victory_sound()
        self.sound_defeat = self._create_defeat_sound()
        self.sound_menu_select = self._create_menu_select_sound()
        self.sound_combat_attack = self._create_combat_attack_sound()
        self.sound_boss_explode = self._create_boss_explode_sound()
        self.sound_player_hit = self._create_player_hit_sound()
    
    def _generate_tone(self, frequency, duration, sample_rate=22050, wave_type='sine'):
        """Génère un ton simple"""
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            if wave_type == 'sine':
                value = math.sin(frequency * 2 * math.pi * t)
            elif wave_type == 'square':
                value = 1.0 if (frequency * t * 2) % 2 < 1 else -1.0
            elif wave_type == 'sawtooth':
                value = 2 * ((frequency * t) % 1) - 1
            else:
                value = math.sin(frequency * 2 * math.pi * t)
            
            self._set_array_value(arr, i, int(value * max_sample * self.volume))
        
        return self._make_sound(arr)
    
    def _create_jump_sound(self):
        """Son de saut (court et aigu)"""
        duration = 0.15
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Fréquence qui monte rapidement (400Hz -> 600Hz)
            freq = 400 + (200 * (i / frames))
            value = math.sin(freq * 2 * math.pi * t) * (1.0 - (i / frames) * 0.5)
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.6))
        
        return self._make_sound(arr)
    
    def _create_enemy_kill_sound(self):
        """Son quand on tue un ennemi (explosion courte)"""
        duration = 0.2
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Mélange de fréquences pour un son d'explosion
            freq1 = 300 * (1.0 - (i / frames))
            freq2 = 150 * (1.0 - (i / frames) * 0.5)
            value = (math.sin(freq1 * 2 * math.pi * t) * 0.6 + 
                    math.sin(freq2 * 2 * math.pi * t) * 0.4) * (1.0 - (i / frames))
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.7))
        
        return self._make_sound(arr)
    
    def _create_collectible_sound(self):
        """Son quand on collecte une étoile (ding joyeux)"""
        duration = 0.25
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Fréquence qui monte puis descend (ding)
            progress = i / frames
            freq = 600 + (200 * math.sin(progress * math.pi))
            value = math.sin(freq * 2 * math.pi * t) * (1.0 - progress * 0.3)
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.5))
        
        return self._make_sound(arr)
    
    def _create_victory_sound(self):
        """Son de victoire (mélodie ascendante)"""
        duration = 0.8
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        # Mélodie de victoire : Do-Mi-Sol-Do (C-E-G-C)
        notes = [523.25, 659.25, 783.99, 1046.50]  # C4, E4, G4, C5
        note_duration = frames // len(notes)
        
        for note_idx, freq in enumerate(notes):
            start_frame = note_idx * note_duration
            end_frame = start_frame + note_duration
            for i in range(start_frame, min(end_frame, frames)):
                t = float(i) / sample_rate
                progress = (i - start_frame) / note_duration
                value = math.sin(freq * 2 * math.pi * t) * (1.0 - progress * 0.2)
                self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.6))
        
        return self._make_sound(arr)
    
    def _create_defeat_sound(self):
        """Son de défaite (ton descendant triste)"""
        duration = 0.5
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Fréquence qui descend (300Hz -> 150Hz)
            freq = 300 - (150 * (i / frames))
            value = math.sin(freq * 2 * math.pi * t) * (1.0 - (i / frames) * 0.5)
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.5))
        
        return self._make_sound(arr)
    
    def _create_menu_select_sound(self):
        """Son de sélection dans le menu (bip court)"""
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            freq = 800
            value = math.sin(freq * 2 * math.pi * t)
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.4))
        
        return self._make_sound(arr)
    
    def _create_combat_attack_sound(self):
        """Son d'attaque en combat (woosh)"""
        duration = 0.15
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Fréquence qui monte rapidement (200Hz -> 400Hz)
            freq = 200 + (200 * (i / frames))
            value = math.sin(freq * 2 * math.pi * t) * (1.0 - (i / frames) * 0.3)
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.5))
        
        return self._make_sound(arr)
    
    def _create_boss_explode_sound(self):
        """Son d'explosion du boss (explosion plus forte)"""
        duration = 0.5
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Mélange de fréquences basses pour une explosion puissante
            freq1 = 200 * (1.0 - (i / frames) * 0.7)
            freq2 = 100 * (1.0 - (i / frames) * 0.5)
            freq3 = 50 * (1.0 - (i / frames) * 0.3)
            value = (math.sin(freq1 * 2 * math.pi * t) * 0.4 + 
                    math.sin(freq2 * 2 * math.pi * t) * 0.3 +
                    math.sin(freq3 * 2 * math.pi * t) * 0.3) * (1.0 - (i / frames) * 0.5)
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.8))
        
        return self._make_sound(arr)
    
    def _create_player_hit_sound(self):
        """Son quand le joueur est touché (bip d'alerte)"""
        duration = 0.2
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = self._make_sound_array(frames)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Fréquence qui oscille rapidement (bip d'alerte)
            freq = 400 + (100 * math.sin(i * 0.1))
            value = math.sin(freq * 2 * math.pi * t) * (1.0 - (i / frames) * 0.4)
            self._set_array_value(arr, i, int(value * max_sample * self.volume * 0.5))
        
        return self._make_sound(arr)
    
    def play_jump(self):
        """Joue le son de saut"""
        if self.sound_enabled:
            self.sound_jump.play()
    
    def play_enemy_kill(self):
        """Joue le son de mort d'ennemi"""
        if self.sound_enabled:
            self.sound_enemy_kill.play()
    
    def play_collectible(self):
        """Joue le son de collectible"""
        if self.sound_enabled:
            self.sound_collectible.play()
    
    def play_victory(self):
        """Joue le son de victoire"""
        if self.sound_enabled:
            self.sound_victory.play()
    
    def play_defeat(self):
        """Joue le son de défaite"""
        if self.sound_enabled:
            self.sound_defeat.play()
    
    def play_menu_select(self):
        """Joue le son de sélection du menu"""
        if self.sound_enabled:
            self.sound_menu_select.play()
    
    def play_combat_attack(self):
        """Joue le son d'attaque en combat"""
        if self.sound_enabled:
            self.sound_combat_attack.play()
    
    def play_boss_explode(self):
        """Joue le son d'explosion du boss"""
        if self.sound_enabled:
            self.sound_boss_explode.play()
    
    def play_player_hit(self):
        """Joue le son quand le joueur est touché"""
        if self.sound_enabled:
            self.sound_player_hit.play()
    
    def set_volume(self, volume):
        """Définit le volume (0.0 à 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        # Recréer les sons avec le nouveau volume
        self._create_sounds()
    
    def enable(self):
        """Active les sons"""
        self.sound_enabled = True
    
    def disable(self):
        """Désactive les sons"""
        self.sound_enabled = False
    
    def toggle(self):
        """Active/désactive les sons"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

