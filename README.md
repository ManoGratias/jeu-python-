# 🎮 Cyber Jump - Plateformer 2D Compétitif

Un jeu de plateforme 2D développé en Python avec Pygame avec un système compétitif complet ! Incarnez un robot cyber dans des courses chronométrées, collectez des récompenses, et affrontez vos adversaires dans des combats stratégiques.

## 📋 Description

**Cyber Jump** est un jeu de plateforme compétitif avec plusieurs modes de jeu :

### 🎯 Mode Classique
- Sauter sur des plateformes pour progresser
- Éviter ou écraser des robots ennemis patrouilleurs
- Collecter des micro-puces pour augmenter votre score
- Atteindre la porte de fin du niveau

### 🏁 Mode Compétitif
- **Courses chronométrées** : Terminez les niveaux le plus vite possible
- **Système de récompenses** : Gagnez des pièces et des items après chaque course
- **Combats stratégiques** : Utilisez vos items pour vaincre vos adversaires
- **3 modes de jeu** :
  - 🆚 **Joueur vs Bot** (5 ou 10 manches)
  - 👥 **Deux joueurs vs Bot** (coopération)
  - ⚔️ **Joueur vs Joueur** (10 manches)
- **Système d'items** : Boost de vitesse, bouclier, double saut, ralentissement

## 🚀 Installation

### Prérequis
- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

   Ou directement :
   ```bash
   pip install pygame
   ```

## 🎯 Lancement du jeu

Pour lancer le jeu, exécutez simplement :

```bash
python main.py
```

Ou sur Windows :
```bash
run.bat
```

Le jeu démarre avec un **écran d'accueil animé** avec le titre "CYBER JUMP" !

## 🕹️ Commandes

### Menu principal
- **Flèches ↑↓** : Naviguer dans le menu
- **Entrée** ou **Espace** : Sélectionner une option

### Pendant le jeu
- **Flèche ←** ou **A** : Déplacer le robot vers la gauche
- **Flèche →** ou **D** : Déplacer le robot vers la droite
- **Espace** : Faire sauter le robot (double saut disponible)
- **ESC** : Retourner au menu principal

### Manette PS4 (optionnelle)
- **Stick gauche** ou **D-Pad** : Déplacer
- **Bouton X** : Sauter
- **Bouton Options** : Menu
- Activez/désactivez dans les Paramètres

### Scoreboard
- **Entrée** ou **ESC** : Retourner au menu principal

### Saisie du pseudo
- **Touches alphanumériques** : Saisir votre pseudo (max 15 caractères)
- **Backspace** : Effacer un caractère
- **Entrée** : Valider et enregistrer le score

## 📊 Règles du jeu

### Objectif
Atteindre la porte verte à la fin du niveau en évitant de perdre toutes vos vies.

### Score
Votre score est calculé à partir de deux éléments :
- **Micro-puces collectées** : +50 points chacune
- **Ennemis écrasés** : +200 points chacun

### Mécaniques
- **Vies** : Vous commencez avec 3 vies
- **Perte de vie** : Vous perdez une vie si vous touchez un ennemi (sans l'écraser) ou si vous tombez en bas de l'écran
- **Écrasement d'ennemis** : Sautez sur un ennemi pour l'éliminer et gagner des points
- **Fin du niveau** : Atteignez la porte verte à droite du niveau pour terminer

### Scoreboard
- Les 10 meilleurs scores sont sauvegardés localement dans `scores.json`
- Chaque score enregistre : le pseudo, le score et la date/heure

## 🏗️ Architecture du code

Le projet est structuré de manière modulaire :

```
.
├── main.py                  # Point d'entrée principal
├── game.py                  # Classe principale gérant les états du jeu
├── config.py                # Configuration et constantes
├── splash_screen.py         # Écran d'accueil animé
├── player.py                # Classe du joueur (robot)
├── enemy.py                 # Classe des ennemis (robots patrouilleurs et volants)
├── boss.py                  # Classe du boss final
├── collectible.py           # Classe des objets collectibles (shurikens)
├── platform.py              # Classe des plateformes
├── level.py                 # Gestion des niveaux (3 niveaux prédéfinis)
├── menu.py                  # Gestion du menu principal
├── scoreboard.py            # Gestion du scoreboard et sauvegarde JSON
├── settings.py              # Gestion des paramètres (manette PS4)
├── settings_menu.py         # Menu des paramètres
├── background.py            # Fond animé avec nuages
├── match_manager.py         # Gestion des manches compétitives
├── race_system.py           # Système de course chronométrée
├── combat_system.py         # Système de combat
├── rewards_system.py        # Système de récompenses
├── items_system.py          # Système d'items et sorts
├── game_modes.py            # Gestion des modes de jeu
├── bot_ai.py                # IA des bots
├── requirements.txt         # Dépendances Python
├── README.md                # Documentation
├── run.bat                  # Script de lancement Windows
└── scores.json              # Sauvegarde des scores (créé automatiquement)
```

### États du jeu
Le jeu gère plusieurs états :
- **menu** : Menu principal
- **playing** : Pendant la partie
- **enter_name** : Saisie du pseudo en fin de partie
- **scoreboard** : Affichage du Top 10
- **game_over** : Écran de fin de partie

### Génération de niveaux
Le système supporte la génération de niveaux depuis un fichier texte (`level.txt`) :
- `1` = Plateforme
- `0` = Vide
- `E` = Ennemi
- `C` = Collectible (micro-puce)
- `F` = Fin du niveau

Si le fichier n'existe pas, un niveau par défaut est généré automatiquement.

## 🎨 Fonctionnalités

### ✅ Fonctionnalités principales
- ✅ **Écran d'accueil animé** avec titre et étoiles
- ✅ Menu complet (Mode Compétitif / Jouer / Scores / Paramètres / Quitter)
- ✅ Contrôles fluides avec physique de saut améliorée
- ✅ **Double saut** activé
- ✅ Système de collisions complet
- ✅ Ennemis avec IA de patrouille (terrestres et volants)
- ✅ Objets collectibles avec animation (shurikens)
- ✅ Score en temps réel basé sur 2 sources
- ✅ Scoreboard Top 10 avec sauvegarde JSON
- ✅ Saisie de pseudo en fin de partie
- ✅ **Support manette PS4** avec activation/désactivation
- ✅ Architecture modulaire et structurée

### 🏆 Mode Compétitif
- ✅ **Système de manches** : Course → Récompenses → Combat
- ✅ **3 modes de jeu** : 1v1, 2v1, PvP
- ✅ **Chronomètre de course** avec HUD dédié
- ✅ **Système de récompenses** : Pièces et items aléatoires
- ✅ **Système de combat** : Barres de vie, attaques, timer
- ✅ **4 types d'items** : Boost vitesse, bouclier, double saut, ralentissement
- ✅ **IA des bots** avec 3 niveaux de difficulté
- ✅ **Progression linéaire** : 3 niveaux avec difficulté croissante
- ✅ **Boss final** : Grand robot avec barre de vie

### 🎯 Conformité au cahier des charges
- ✅ Menu : Jouer / Scores / Quitter
- ✅ Scène jouable complète
- ✅ Contrôles fonctionnels (déplacements + saut)
- ✅ Ennemis avec collision et mécanique d'écrasement
- ✅ Objets ramassables (micro-puces)
- ✅ Score affiché en temps réel
- ✅ Score basé sur 2 éléments (collectibles + ennemis)
- ✅ Saisie de pseudo en fin de partie
- ✅ Scoreboard Top 10
- ✅ Sauvegarde locale (JSON)
- ✅ Écran dédié aux scores
- ✅ Code structuré avec classes
- ✅ Gestion des états (menu / jeu / fin / scores)
- ✅ README complet

## 🔧 Personnalisation

### Modifier les paramètres du jeu
Tous les paramètres sont centralisés dans `config.py` :
- Taille de l'écran
- Vitesse du joueur
- Force de saut
- Gravité
- Scores des collectibles et ennemis
- Couleurs

### Créer vos propres niveaux
Créez un fichier `level.txt` avec le format décrit ci-dessus pour générer vos propres niveaux.

## 🐛 Dépannage

### Le jeu ne démarre pas
- Vérifiez que Python 3.7+ est installé
- Vérifiez que pygame est installé : `pip install pygame`

### Erreur de module non trouvé
- Assurez-vous que tous les fichiers `.py` sont dans le même dossier
- Vérifiez que vous lancez le jeu depuis le bon répertoire

### Le scoreboard ne s'affiche pas
- Le fichier `scores.json` sera créé automatiquement lors de la première partie terminée

## 📝 Notes pour la présentation

### Points à mettre en avant
1. **Architecture modulaire** : Code organisé en classes séparées pour chaque entité
2. **Gestion des états** : Système d'états propre pour menu/jeu/scores
3. **Physique de saut** : Implémentation de la gravité et des collisions
4. **Système de score** : Score basé sur 2 sources différentes
5. **Persistance** : Sauvegarde des scores en JSON
6. **Génération de niveaux** : Possibilité de créer des niveaux depuis un fichier texte

### Démonstration suggérée
1. Montrer le menu principal
2. Jouer une partie complète
3. Montrer la collecte de micro-puces
4. Montrer l'écrasement d'un ennemi
5. Terminer le niveau et saisir un pseudo
6. Afficher le scoreboard

## 📄 Licence

Ce projet est réalisé dans le cadre d'un projet académique.

## 👨‍💻 Auteur

Projet développé avec Python et Pygame.

---

**Bon jeu et bonne chance pour votre présentation ! 🚀**
