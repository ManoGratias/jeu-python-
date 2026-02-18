# 🚀 Guide Simple : Créer le dépôt sur GitHub

## Étape 1 : Créer le dépôt sur GitHub

1. **Allez sur** : https://github.com/new
   - Ou cliquez sur le bouton vert "New" en haut à droite de votre profil

2. **Remplissez le formulaire** :
   - **Repository name** : `Cyber-Jump`
   - **Description** (optionnel) : `Plateformer 2D Compétitif avec système de manches, combats et items`
   - **Visibilité** : Choisissez Public ou Private
   - ⚠️ **IMPORTANT** : Ne cochez PAS "Add a README file" (nous en avons déjà un)
   - ⚠️ **IMPORTANT** : Ne cochez PAS "Add .gitignore" (nous en avons déjà un)
   - ⚠️ **IMPORTANT** : Ne cochez PAS "Choose a license"

3. **Cliquez sur** : "Create repository" (bouton vert en bas)

## Étape 2 : Créer un Token d'Accès Personnel

1. **Allez sur** : https://github.com/settings/tokens
   - Ou : GitHub → Votre profil (en haut à droite) → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Cliquez sur** : "Generate new token" → "Generate new token (classic)"

3. **Remplissez** :
   - **Note** : `Cyber-Jump` (ou n'importe quel nom)
   - **Expiration** : Choisissez une durée (90 jours, 1 an, etc.)
   - **Scopes** : Cochez **"repo"** (cela cochera automatiquement toutes les sous-options)

4. **Cliquez sur** : "Generate token" (en bas de la page)

5. **⚠️ COPIEZ LE TOKEN IMMÉDIATEMENT** (vous ne le reverrez qu'une fois !)
   - Il ressemble à : `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Étape 3 : Pousser le code

Ouvrez PowerShell ou CMD dans le dossier du projet et exécutez :

```bash
cd "c:\Users\hkounou\Documents\jeu python"
git push -u origin main
```

Quand il demande :
- **Username** : `ManoGratias`
- **Password** : **Collez votre TOKEN** (pas votre mot de passe GitHub normal)

## ✅ Vérification

Après le push, votre dépôt sera visible sur :
**https://github.com/ManoGratias/Cyber-Jump**

---

## 🔧 Alternative : Utiliser GitHub Desktop

Si vous préférez une interface graphique :

1. Téléchargez GitHub Desktop : https://desktop.github.com/
2. Connectez-vous avec votre compte GitHub
3. File → Add Local Repository
4. Sélectionnez le dossier "jeu python"
5. Cliquez sur "Publish repository"

