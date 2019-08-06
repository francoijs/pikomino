import copy
import numpy as np
from state import State as Base


class State(Base):
    
    def __init__(self, player_starts=True):
        self.cells = [None] * 9
        self.player = '0' if player_starts else '1'

    def __eq__(self, other):
        return self.cells == other.cells

    def __repr__(self):
        grid  = '\n([\t'+str(self.cells[0])+'\t'+str(self.cells[1])+'\t'+str(self.cells[2])+'\n'
        grid += '\t'+str(self.cells[3])+'\t'+str(self.cells[4])+'\t'+str(self.cells[5])+'\n'
        grid += '\t'+str(self.cells[6])+'\t'+str(self.cells[7])+'\t'+str(self.cells[8])+'],\t'
        grid += self.player+')'
        return grid
    
    positions = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]

    def winner(self):
        for pos in State.positions:
            symbol = self.cells[pos[0]]
            winner = symbol
            for i in pos:
                if self.cells[i] != symbol:
                    winner = None
                    break
            if winner != None:
                return winner
        return None

    def end_of_game(self):
        winner = self.winner()
        if winner:
            return True
        if None not in self.cells:
            # draw
            return True
        return False

    def turn_of_player(self):
        return self.player == '0'

    def player_wins(self):
        return self.winner() == '0'
    def opponent_wins(self):
        return self.winner() == '1'

    def player_score(self):
        return 1 if self.player_wins() else 0
    def opponent_score(self):
        return 1 if self.opponent_wins() else 0
    
    def transition(self, action):
        """ Apply action on state and return new state. """
        state = copy.deepcopy(self)
        state.cells[action] = self.player
        # next player
        state.player = str(1 - int(self.player))
        # end of turn
        return state

    def report(self, name, prev_state):
        pass
    
    def find_candidates(self):
        """ Return list of candidates actions """
        r = []
        for i in range(len(self.cells)):
            if self.cells[i] is None:
                r.append(i)
        return r

    
    INPUTS = 27
    OUTPUTS = 9

    def inputs(self):
        res = np.zeros((1, self.INPUTS))
        for i in range(len(self.cells)):
            if not self.cells[i]:
                res[0, 3*i] = 1
            elif self.cells[i] == self.player:
                res[0, 3*i+1] = 1
            else:
                res[0, 3*i+2] = 1
        return res

