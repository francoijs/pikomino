# A DQN playing Pikomino

**Requires dependencies:**
keras, numpy


**To play against the trained model:**

    $ ./play.py best_strategy.h5

You play first.

__Example of turn:__

    state: ([23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35],[22],[25, 21, 24],[3, 0, 0, 0, 2, 0],[0, 0, 0, 1, 2, 0]) / total: 23
    choose action [3, 9]: 

__Content of state:__
- the 1st array is the available tiles (the stash),
- the 2nd array [22] is the tiles taken by the opponent (in that order),
- the 3rd array [25, 21, 24] is the tiles you already won (in that order),
- the 4th array [3, 0, 0, 0, 2, 0] is the dices you have chosen: here you have 3 worms and 2 4's
- the 5th array [0, 0, 0, 1, 2, 0] is the dices that have just been rolled: here 1 3 and 2 4's.
The total 23 is the number of points in the dices that have been chosen (3 * 5 + 2 * 4)

__Actions:__
- actions below 6 mean choosing a dice value and re-rolling: 0 to keep the worms, ..., 5 to keep the 5's, then roll again
- actions >= 6 mean choosing a dice value and keeping (or stealing) the corresponding tiles. This ends the turn.
- if no actions are available, the turn (and a tile) is automatically lost 


**To train a new model:**

    $ ./train.py  -e 5000 -s 500 -l4

Trains for 5000 episodes (5000 games of 2 players, the model plays both players).
Every 500 episodes, the model is evaluated and saved.
The model will have 4 hidden layers of 103 cells. 103 is the width of the input layer (which represents the encoded state), and the default size of hidden layers.
The output layer always has 12 cells (which represent the q-values for each 12 actions).
