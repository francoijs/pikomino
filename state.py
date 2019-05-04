import random, bisect, copy
import numpy as np


def _roll(n):
    """ Roll n dices and return 6-array with count for each value """
    roll = [0,0,0,0,0,0]
    draw = [random.randint(0,5) for _ in range(n)]
    for d in draw:
        roll[d] += 1
    return roll

def score(tiles):
    """ Return score yielded by a set of tiles """
    score = 0
    for t in tiles:
        if   t<25: score += 1
        elif t<29: score += 2
        elif t<33: score += 3
        else:      score += 4
    return score

class sortedlist(list):
    '''just a list but with an insort (insert into sorted position)'''
    def insort(self, x):
        bisect.insort(self, x)

class State(object):
    
    def __init__(self, stash=range(21,37),
                 opponent=None, player=None,
                 dices=[0,0,0,0,0,0], roll=None):
        if not roll:
            roll = _roll(8)
        if not player:
            player = []
        if not opponent:
            opponent = []    
        self.stash    = sortedlist(stash)
        self.opponent = opponent
        self.player   = player
        self.dices    = copy.copy(dices)
        self.roll     = roll

    def __eq__(self, other):
        return self.stash==other.stash and self.opponent==other.opponent and self.player==other.player and self.dices==other.dices

    def __repr__(self):
        return '('+str(self.stash)+','+str(self.opponent)+','+str(self.player)+','+str(self.dices)+','+str(self.roll)+')'

    def lose_tile(self):
        if self.player:
            # lose 1 tile
            self.stash.insort(self.player.pop())
        if self.stash:
            # remove biggest tile
            self.stash.pop()
        # end of turn
        return self.end_turn()

    def end_turn(self):
        self.roll = _roll(8)
        self.dices = [0,0,0,0,0,0]
        return self, self.get_reward()

    def end_of_game(self):
        return not self.stash
    def end_of_turn(self):
        return sum(self.dices) == 0
            
    def total(self):
        return 5*self.dices[0] + sum([n*self.dices[n] for n in range(6)])

    def change_turn(self):
        return State(stash=self.stash,
                     opponent=self.player,
                     player=self.opponent)

    def player_wins(self):
        return score(self.player) > score(self.opponent)
    def opponent_wins(self):
        return score(self.player) < score(self.opponent)

    def player_score(self):
        return score(self.player)
    def opponent_score(self):
        return score(self.opponent)

    
    def transition(self, action):
        """ Apply action on state and return new state. """
        if action == -1:
            # give back 1 tile
            return self.lose_tile()
        if action<6:
            # keep some dices then reroll
            self.dices[action] += self.roll[action]
            self.roll = _roll(8-sum(self.dices))
            return self, 0
        else:
            self.transition(action-6)
            if self.opponent and self.total()==self.opponent[-1]:
                # take tile of opponent
                self.player.append(self.opponent.pop())
            else:
                # take tile from stash?
                tile = self.total()
                while tile > 20:
                    if tile in self.stash:
                        self.stash.remove(tile)
                        break
                    tile -= 1
                if tile == 20:
                    # no tile available with this total -> give back 1 tile
                    return self.lose_tile()
                self.player.append(tile)
        # end of turn
        return self.end_turn()

    def get_reward(self):
        # reward?
        if self.stash:
            return 0
        else:
            if self.player_wins():
                return 1
        return -1
    
    def find_candidates(self):
        """ Return list of candidates actions """
        assert sum(self.dices) + sum(self.roll) == 8
        # dices that may be kept before rerolling
        candidates = [n for n in range(6) if self.roll[n]>0 and self.dices[n]==0]
        # dices that may be kept before stopping
        stop = []
        for action in candidates:
            if action==0:
                new_score = self.total() + self.roll[0]*5
                if new_score>=self.stash[0] or (self.opponent and self.opponent[-1]==new_score):
                    stop.append(6)
            else:
                # cannot stop if score not at least bigger than the smallest available tile
                new_score = self.total() + self.roll[action]*action
                if action and not self.dices[0]:
                    new_score = 0
                if self.stash and (new_score>=self.stash[0] or (self.opponent and self.opponent[-1]==new_score) ):
                    stop.append(6+action)
        return candidates + stop

    
    # ohv: 16 possible tiles in stash
    # ohv: 16 possible top opponent tiles [21,36]
    # ohv: 16 possible top mine tiles [21,36]
    # ohv: possible score delta [-40,40]
    # 2 sets: dices kept + dices rolled
    # per set: 6 sides * [0-8] count of dices per side
    INPUTS = 16+16+16+81+2*6*9   # 237
    # 12 possibles actions: keep 1 of 6 sides and reroll or stop
    OUTPUTS = 12

    def inputs(self):
        res = np.zeros((1, self.INPUTS))
        ptr = 0
        # stash
        for t in self.stash:
            res[0,ptr+t-21] = 1
        ptr += 16
        # opponent top tile
        if self.opponent:
            res[0,ptr+self.opponent[-1]-21] = 1
        ptr += 16
        # my top tile
        if self.player:
            res[0,ptr+self.player[-1]-21] = 1
        ptr += 16
        # score delta
        res[0,ptr+40+self.player_score()-self.opponent_score()] = 1
        ptr += 81
        # dices
        for s in range(6):
            res[0,ptr+s*9+self.dices[s]] = 1
        ptr += 6*9
        # roll
        for s in range(6):
            res[0,ptr+s*9+self.roll[s]] = 1
        ptr += 6*9
        assert ptr == self.INPUTS
        return res
