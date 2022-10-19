# Quickstart

## Playing a game of chess in a Jupyter notebook

### 2 Human Players (or yourself) playing a game

```python
from beth.game import Game
from beth.players.random_player import RandomPlayer
from beth.players.human_player import HumanPlayer

# Instantiate player and game
white = HumanPlayer()
black = HumanPlayer()
game = Game(white,black)

# Run the game to play in the notebook
game.run()
```

### Playing from a game checkpoint (after a list of moves)
```python
game = Game(white,black)
scores = game.move(["e4","d5","d5","g8f6","d4","f6d5"])
```
The engine use ``python-chess`` to display the board as SVG and parse SAN (standard algebric notation) moves. 

It also returns the ``scores``, ie the points for each move, with the standard conventions (and positive for white and negative for black captures)

- 1 for a pawn captured
- 3 for a bishop or a knight
- 5 for a rook
- 9 for a queen
- 200 for a king checkmated

In the example above, 
```python
scores
>>> [0,0,1,0,0,-1]
```

## Playing against a chess engine

!!! warning
    Under construction

