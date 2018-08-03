#!/usr/bin/python

import time, sys, argparse, random, signal
import numpy as np
from q_hash import HashQ
from train import train
from algo import algo_qlearning


tot_rounds = tot_score = won = episodes = 0


def _roll(n):
    """ Roll n dices and return 6-array with count for each value """
    roll = [0,0,0,0,0,0]
    draw = [random.randint(0,5) for _ in range(n)]
    for d in draw:
        roll[d] += 1
    return roll


class State():
    
    def __init__(self):
        self.dices = [0,0,0,0,0,0]
        self.roll  = _roll(8)
        self._end = self._won = False

    def __repr__(self):
        return '('+str(self.dices)+','+str(self.roll)+')'
    
    def end_of_game(self):
        return self._end

    def player_wins(self):
        return self._won
    def player_score(self):
        return self.total()
    
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
                if new_score>20:
                    stop.append(6)
            else:
                # cannot stop if score not at least bigger than 21
                new_score = self.total() + self.roll[action]*action
                if action and not self.dices[0]:
                    new_score = 0
                if new_score>20:
                    stop.append(6+action)
        return candidates + stop
    
    def transition(self, action):
        """ Apply action on state and return new state. """
        if action == -1:
            # roll is lost
            self._end = True
            self._won = False
            return self, -1
        if action<6:
            # keep some dices then reroll
            self.dices[action] += self.roll[action]
            self.roll = _roll(8-sum(self.dices))
            return self, 0
        else:
            # keep som dices then stop
            self.transition(action-6)
            self._end = True
            self._won = True
            # normalize reward between 0 and 1
            return self, float(self.total()-20)/16

    def total(self):
        return 5*self.dices[0] + sum([n*self.dices[n] for n in range(6)])

    INPUTS = 2*6*9
    # 12 possibles actions: keep 1 of 6 sides and reroll or stop
    OUTPUTS = 12

    def inputs(self):
        res = np.zeros((1, self.INPUTS))
        ptr = 0
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

    
class EpisodeRoll():

    dbname = 'roll'

    @staticmethod
    def episode(q, q_opponent=None, algo=algo_qlearning):
        # initial state & action
        state = State()
        action = -1
        rounds = 0
        while True:
            state,action = algo(q, state, action)
            rounds += 1
            if state.end_of_game():
                # game is over
                break
        # stats
        global tot_rounds, tot_score, won, episodes
        episodes += 1
        if state.player_wins():
            won += 1
            tot_score += state.player_score()  
        tot_rounds += rounds  
        return state, 0, rounds

    @staticmethod
    def print_stats():
        global tot_rounds, tot_score, won, episodes
        if won:
            avg_score = float(tot_score)/won
        else:
            avg_score = 0
        return 'avg score: %.1f' % (avg_score,)

    @staticmethod
    def reset_stats():
        global tot_rounds, tot_score, won, episodes
        tot_rounds = tot_score = won = episodes = 0


if __name__ == "__main__":
    train(argparse.ArgumentParser(description='Train to roll the dices (min score=21).'),
          EpisodeRoll, State)
