# Jeu de Rôle Fantasy Tactique

[![Conçu avec Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)\
[![Licence](https://img.shields.io/github/license/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/blob/master/LICENSE)\
[![Dernière version](https://img.shields.io/github/v/release/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/releases/latest)\
![Téléchargements totaux de la dernière version sur GitHub](https://img.shields.io/github/downloads/Grimmys/rpg_tactical_fantasy_game/latest/total)

**Ouvert au développement collaboratif.**

Le jeu est un RPG de fantasy tactique, au tour par tour et en 2D.

## Comment aider au développement

Vous pouvez envoyer vos demandes ou signaler un bogue par courriel à **grimmys.programming@gmail.com** ou ouvrir une *issue* sur GitHub.

Vous pouvez aussi rejoindre le serveur Discord de la communauté : https://discord.gg/CwFdXNs9Wt

N'hésitez pas à proposer des idées, qu'elles portent sur les pratiques de codage ou les mécaniques de jeu : ce projet est loin d'être parfait !

Voici quelques pistes de contribution :

- Consulter les [issues ouvertes](https://github.com/Grimmys/rpg_tactical_fantasy_game/issues) ; certains bogues peuvent être corrigés et plusieurs améliorations sont en attente.
- De nombreux **TODO** parsèment le projet ; certains sont accessibles aux débutants, d'autres sont plus exigeants.
- Aider à l'équilibrage du jeu serait très apprécié... Ce n'est pas mon point fort, même si j'adore ce type de jeux. Toutes les valeurs se trouvent dans les fichiers XML du dossier **data**.
- Les contributions en effets sonores ou en nouvelles bandes-son sont également les bienvenues.

#### Gérer les ressources volumineuses avec Git LFS

Si vous prévoyez d'ajouter de nouvelles images, pistes audio ou polices, pensez à activer Git LFS (Large File Storage) avant de valider vos commits :

```bash
git lfs install
git lfs track "*.png" "*.wav" "*.ttf"
git add .gitattributes
```

__Version__ : 1.0.4

![Écran principal avec les déplacements et attaques possibles](/screenshots/player_moves_and_attacks.png?raw=True)\
![Menu d'inventaire](/screenshots/inventory_screen.png?raw=True)\
![Fenêtre d'état](/screenshots/status_screen.png?raw=True)

## Comment démarrer le jeu

Si vous utilisez Windows 64 bits, rendez-vous sur la [page des publications](https://github.com/grimmys/rpg_tactical_fantasy_game/releases) pour récupérer l'exécutable précompilé.

Si vous préférez exécuter le jeu à partir du code source (ou contribuer à son développement), assurez-vous d'avoir installé [Python 3.13](https://python.org) (ou une version plus récente) ainsi que [uv](https://docs.astral.sh/uv/getting-started/installation/).

Ensuite, depuis le dossier du dépôt git, lancez `uv run main.py` pour démarrer le jeu.

## Commandes

- Clic gauche : sélectionner un joueur, choisir une case, lancer une action, etc. (bouton principal)
- Clic gauche (sur une case vide) : ouvrir ou fermer le menu principal
- Clic gauche (sur toute entité qui n'est pas un joueur ayant terminé son tour) : afficher une fenêtre d'informations sur l'entité
- Clic droit : désélectionner un joueur ou annuler la dernière action si possible (bouton secondaire)
- Clic droit (sur n'importe quelle entité) : afficher ses déplacements possibles
- Touche Esc : fermer le menu situé au premier plan
