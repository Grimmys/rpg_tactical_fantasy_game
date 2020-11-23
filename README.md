# RPG Tactical Fantasy Game

<b>WARNING</b> : This game is entirely under construction.

The game is an RPG Tactical Fantasy game, turn-based and is in 2D.
I'm currently looking for a good name.

## How to help development

You can submit any request you want, or notify me about any bug you encountered, by sending an e-mail to grimmys.programming@gmail.com or by opening an issue.
<br>

Please, don't hesitate about suggesting ideas : it's my first " serious " game project. ;)

<ul>
  <li> Help with balancing would be greatly appreciated... I'm not really good in this kind of games even if I love them !
  All values could be found in the XML files wrapped in the data folder. </li>
  <li> Since I'm not a designer, some elements may be oddly placed in the UI. You can try to correct the ones you see or simply notify me. </li>
  <li> Contributions for sound effects / soundtracks would be really appreciated ! </li>
  <li> Ideas about future levels could be submitted, however, I'm currently working on a scenario. </li>
 </ul>

<b>Version</b> : 1.0.3

![Main screen with possible moves and attack](/screenshots/player_moves_and_attacks.png?raw=True)
![Inventory menu](/screenshots/inventory_screen.png?raw=True)
![Status window](/screenshots/status_screen.png?raw=True)

## How to start the game

Type the following command in a shell at the project root :

``python main.py``

Make sure to have python and pygame installed.

If you don't have python, you can just execute ``build/exe.win32-3.6/main.exe``.

## Keys

* Left click : Select a player, choose a case to move, select an action to do etc (main button)
* Left click (on any empty tile) : Open main menu
* Left click (on any entity that is not a player who has finished his turn) : Open a window giving information about the entity
* Right click : Deselect a player or cancel last action if possible (secondary button)
* Right click (on any entity) : Show the possible movements of the entity
