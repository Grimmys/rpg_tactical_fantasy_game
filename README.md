# RPG Tactical Fantasy Game

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![licence](https://img.shields.io/github/license/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/blob/master/LICENSE)
[![latest release](https://img.shields.io/github/v/release/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/releases/latest)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/Grimmys/rpg_tactical_fantasy_game/latest/total)

[ [English](README.md) | [简体中文](README/zh-cn.md) | [繁體中文](README/zh-cht.md) ]

**Open to collaborative development.**

The game is a Tactical Fantasy RPG, turn-based and in 2D.

## How to help development

You can submit any request you want, or report any bug you encounter, by sending an e-mail to
grimmys.programming@gmail.com or by opening an issue.

Alternatively, you can join the newly created community discord: https://discord.gg/CwFdXNs9Wt.

Feel free to come up with ideas whether it is about coding practices or game mechanics, this project is far from being
perfect!

Here are some suggestions of contributions:

* Check the [opened issues](https://github.com/Grimmys/rpg_tactical_fantasy_game/issues), there are bugs that could be
  fixed or enhancement waiting for implementation.
* A lot of TODOs can be found everywhere on the project, some of them could be easy to fix even by a beginner and others
  are more challenging.
* Help with balancing would be greatly appreciated... I'm not good in this kind of games even if I love them. All values
  could be found in the XML files wrapped in the data folder.
* Contributions for sound effects or new soundtracks would be really appreciated.

__Version__ : 1.0.4

![Main screen with possible moves and attack](/screenshots/player_moves_and_attacks.png?raw=True)
![Inventory menu](/screenshots/inventory_screen.png?raw=True)
![Status window](/screenshots/status_screen.png?raw=True)

## How to start the game

If you are using 64-bit Windows you can head over to
the [releases page](https://github.com/grimmys/rpg_tactical_fantasy_game/releases) to get a prebuilt executable.

If you would rather run directly from the source \(or want to develop the game\), make sure to
have [Python3.9](https://python.org) (or above) installed and run `python -m pip install -r requirements` in the repository folder.

Then you can run `python main.py` or "./main.py" (only for Python 3) in linux operation system to start the game.

## Keys

* Left click : Select a player, choose a case to move, select an action to do etc (main button)
* Left click (on any empty tile) : Open or close main menu
* Left click (on any entity that is not a player who has finished his turn) : Open a window giving information about the
  entity
* Right click : Deselect a player or cancel last action if possible (secondary button)
* Right click (on any entity) : Show the possible movements of the entity
* Esc key : Close a menu on the top layer
