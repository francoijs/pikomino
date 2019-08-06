import random
import copy
import numpy
from state import State


class StateTest(State):

    INPUTS = 3
    OUTPUTS = 3
    
    def __init__(self, player_starts=True):
        self.cells = [0,0,0]
        self.player = 1 if player_starts else 2
    def __repr__(self):
        return str((self.cells, self.player))
    
    def find_candidates(self):
        res = []
        for i in range(len(self.cells)):
            if self.cells[i] == 0:
                res.append(i)
        return res

    def end_of_game(self):
        if 0 in self.cells:
            return False
        return True

    def change_turn(self):
        return self

    def turn_of_player(self):
        return self.player == 1

    def player_wins(self):
        return self.cells[0] == self.cells[1] == 1 or self.cells[1] == self.cells[2] == 1
    def player_score(self):
        return 1 if self.player_wins() else 0
    def opponent_wins(self):
        return self.cells[0] == self.cells[1] == 2 or self.cells[1] == self.cells[2] == 2
    def opponent_score(self):
        return 1 if self.opponent_wins() else 0
    def draw(self):
        return self.end_of_game() and not self.player_wins() and not self.opponent_wins()
    
    def transition(self, action):
        assert action>=0 and action<3
        assert self.cells[action] == 0
        state = copy.deepcopy(self)
        state.cells[action] = self.player
        state.player = 3-self.player
        return state

    def inputs(self):
        # 1 is player, 2 is opponent
        return numpy.asarray([1 if (c == self.player) else 0 if (c == 0) else 2
                              for c in self.cells]
        ).reshape(1,3)
