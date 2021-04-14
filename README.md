# RPG Tactical Fantasy Game

__WARNING__ : This game is entirely under construction.

The game is an RPG Tactical Fantasy game, turn-based and is in 2D.
I'm currently looking for a good name.

## How to help development

You can submit any request you want, or notify me about any bug you encountered, by sending an e-mail to grimmys.programming@gmail.com or by opening an issue.

Please, don't hesitate about suggesting ideas : it's my first " serious " game project. ;)

* Help with balancing would be greatly appreciated... I'm not really good in this kind of games even if I love them !
  All values could be found in the XML files wrapped in the data folder.
* Since I'm not a designer, some elements may be oddly placed in the UI. You can try to correct the ones you see or simply notify me.
* Contributions for sound effects / soundtracks would be really appreciated !
* Ideas about future levels could be submitted, however, I'm currently working on a scenario.

__Version__ : 1.0.4

![Main screen with possible moves and attack](/screenshots/player_moves_and_attacks.bmp?raw=True)
![Inventory menu](/screenshots/inventory_screen.bmp?raw=True)
![Status window](/screenshots/status_screen.bmp?raw=True)

## How to start the game

If you are using 64-bit Windows you can head over to the [releases page](https://github.com/grimmys/rpg_tactical_fantasy_game/releases) to get a prebuilt executable.

If you would rather run directly from the source \(or want to develop the game\), make sure to have [Python](https://python.org) installed and run `python -m pip install -r requirements.txt` in the repository folder.

Then you can run `python main.py` to start the game.

## Keys

* Left click : Select a player, choose a case to move, select an action to do etc (main button)
* Left click (on any empty tile) : Open main menu
* Left click (on any entity that is not a player who has finished his turn) : Open a window giving information about the entity
* Right click : Deselect a player or cancel last action if possible (secondary button)
* Right click (on any entity) : Show the possible movements of the entity
