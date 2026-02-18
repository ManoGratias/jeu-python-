# Instructions pour pousser le code sur GitHub

## Méthode 1 : Avec un Token d'Accès Personnel (Recommandé)

1. **Créer le dépôt sur GitHub** :
   - Allez sur https://github.com/new
   - Nom : `Cyber-Jump`
   - Description : "Plateformer 2D Compétitif avec système de manches, combats et items"
   - Ne cochez PAS "Initialize with README"
   - Cliquez sur "Create repository"

2. **Créer un Token d'Accès** :
   - Allez sur https://github.com/settings/tokens
   - Cliquez sur "Generate new token" → "Generate new token (classic)"
   - Nom : "Cyber-Jump"
   - Cochez "repo" (accès complet)
   - Cliquez sur "Generate token"
   - **COPIEZ LE TOKEN** (vous ne le reverrez qu'une fois !)

3. **Pousser le code** :
   ```bash
   cd "c:\Users\hkounou\Documents\jeu python"
   git push -u origin main
   ```
   Quand il demande le username : entrez `ManoGratias`
   Quand il demande le password : **collez votre token** (pas votre mot de passe GitHub)

## Méthode 2 : Avec GitHub CLI (gh)

Si vous avez GitHub CLI installé :
```bash
gh auth login
gh repo create Cyber-Jump --public --source=. --remote=origin --push
```

## Méthode 3 : Avec SSH (Plus sécurisé, mais nécessite une clé SSH)

1. Configurez une clé SSH sur GitHub
2. Changez l'URL du remote :
   ```bash
   git remote set-url origin git@github.com:ManoGratias/Cyber-Jump.git
   git push -u origin main
   ```

## Vérification

Après le push, votre code sera disponible sur :
**https://github.com/ManoGratias/Cyber-Jump**

