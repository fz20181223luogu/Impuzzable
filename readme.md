This is a game about the puzzle [Impuzzable](https://nrich.maths.org/articles/impuzzable).

Your goal for each puzzle is to assemble all jigsaw pieces to form a rectangle/square.

There are 25 levels to challenge, with board sizes of 3x3, 3x4 and 4x4

# To start the program
Make sure you have [Python](https://www.python.org) and [pygame](https://www.pygame.org) installed on your computer.

The font used by the game is `avenirltproheavy`, you can run the game without that font and use default font instead.

Then run `game.py` to start the game. Make sure the program is being run at the folder where `Puzzle.py`, `Generator.py`, `level.json`, and `pattern.json` are located, as the game relies on these files.

# Usage
The game consists of 3 pages: Main page, Level selection page and Game page.

## Main page
Click the play button to select levels.

Random boards of size 3x3, 3x4 and 4x4 are also offered. However, due to the complexity of verifying solutions, a 4x4 board will likely have no solutions as the verify process is skipped for that size.

## Level selection page
Click the level to enter the corresponding level.

Click `back` button to go back to main page.

# Game page

Click the selection area (grid at the right side) to select pieces.
* Selected piece are highlighted in green.
* if a selected piece is clicked, such piece will rotate $90^\circ$ anticlockwise. A reminder that you cannot flip a piece in this game.
* Click a blank place to deselect any piece.

With a piece being selected, click a tile on the board (grid at the left side) to exchange the piece on the tile clicked, and the piece being selected.
* Either selection can be empty, which add/remove a piece from the puzzle.
* If the new piece being selected cannot fit the new place, an exchange will not be performed.
* If no piece is being selected, nothing will happen.

Click the arrow button under the board to shift all blocks 1 unit to the indicated direction, provided there are enough space.
* if there is no enough space, the action will not perform.

Click the `Rotate CW/CCW` button to rotate the entire board $90^\circ$ clockwise/counterclockwise.
* For a rectangle board the rotation degree will be $180^\circ$ , which clicking either button will have the same effect.

Click the `Show solution` button to see solution overlaying the board but under the puzzle pieces, and click `Hide solution` to hide them.
* First time calling this button may cause a little glitch, as solution is being calculated during that time.
* If there are no solutions the text `No Solution...` will be shown.

Click the back button to go back to the level selection page.

# Other Tools
The game uses `Puzzle.py` and  `Generator.py` for puzzle-related support and level generate support. By running them individually, `Puzzle.py` will act as a solver to the given puzzle, and `Generator.py` will generate desired level with indicated amount.

Functions and classes in these files can also be called individually as tools. Further details please refer to the docstring of each function.

## Input specifications
The `Puzzle.py` follows following input specifications:
* First line consists two integers $n$ and $m$, as the height and width of the puzzle.
* For the following $n\times m$ lines, each line consist of $4$ integers, as the up, right, down, and left side's concave shape id
    * By default up and right are concave out, down and left are concave in
* A visualized adjacent shape id can be found below:
```
+---------------------+
|                     |
|       adj[0]        |
|        (+)          |
|                     |
|adj[3]        adj[1] |
| (-)           (+)   |
|                     |
|       adj[2]        |
|        (-)          |
+---------------------+
```

The `Generator.py` follows following input specifications:
* First line consists five integers $n$, $m$, $p$, $sol$, and $num$, This will generate $num$ number of puzzle with parameters $n$, $m$, $p$, and $sol$. More details about those parameters can be found at the docstring of function `GenData`
