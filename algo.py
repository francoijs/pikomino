import copy
import logging
import random
import math
import numpy as np
from policy import PolicyExploit
from q_hash import MemoryOnlyHashQ


log = logging.getLogger('algo')


class Algo(object):
    
    ALPHA       = 0.3    # learning rate
    
    def set_params(self, alpha):
        self.ALPHA = alpha
        log.debug('algo: alpha=%.2f', self.ALPHA)


class AlgoQLearning(Algo):

    def __init__(self, q, alpha=.3):
        self.ALPHA = alpha
        self.q = q
        self.opponent_policy = PolicyExploit(q)
        self.sum_td_error = 0
        self.count_td_error = 0
        log.info('q-learning: alpha=%.2f', self.ALPHA)

    def get_stats(self):
        if self.count_td_error:
            return float(self.sum_td_error)/self.count_td_error
        return 0

    def reset_stats(self):
        self.sum_td_error = self.count_td_error = 0

    def update(self, state0, state, action, reward):
        allq0 = self.q.get_all(state0.inputs())
        allq  = self.q.get_all(state.inputs())
        if state.end_of_game():
            qsa = reward
        elif allq[0].any():
            qsa = max([allq[0,a] for a in state.find_candidates()])
        else:
            qsa = 0
        old = allq0[0,action]
        tde = reward + qsa - old
        new = old + self.ALPHA * tde
        self.q.set(state0.inputs(), action, new, allq0)
        log.debug('updated %s,%d: %s -> %s', state0, action, old, new)
        
        

    # def update(self, policy, state, action):
    #     # turn of player
    #     state0 = copy.deepcopy(state)
    #     action0,candidates,allq0 = policy.play(state)
    #     if action == -1:
    #         action = action0
    #     state,reward = state.transition(action)
    #     # end of game?
    #     if reward:
    #         # terminal step -> game over
    #         qsa = 0
    #     else:
    #         # game not over
    #         # turn of opponent
    #         action1, _, _ = self.opponent_policy.play(state)
    #         state,reward = state.transition(action1)
    #         # end of game?
    #         qsa = 0
    #         if state.end_of_game():
    #             if not state.draw():
    #                 reward = -reward
    #         else:
    #             allq = policy.q.get_all(state.inputs())
    #             qsa = max([allq[0,a] for a in candidates])
    #     # update q(state0,action) if training is active
    #     if self.ALPHA and action!=-1:
    #         old = allq0[0,action]
    #         tde = reward + qsa - old
    #         new = old + self.ALPHA * tde
    #         policy.q.set(state0.inputs(), action, new, allq0)
    #         log.debug('updated %s,%d: %s -> %s', state0, action, old, new)
    #     else:
    #         tde = 0
    #     self.sum_td_error += math.fabs(tde)
    #     self.count_td_error += 1
    #     # log transition
    #     log.debug('transition: %s --|%d|-> %s , reward: %d', state0, action, state, reward)
        
    #     return state, -1



class AlgoSarsa(Algo):

    def __init__(self, alpha=.3):
        self.ALPHA = alpha
        self.sum_td_error = 0
        self.count_td_error = 0

    def update(self, policy, state, action):
        state0 = copy.deepcopy(state)
        action0,candidates,allq0 = policy.play(state)
        if action == -1:
            action = action0
        state,reward = state.transition(action)
        action1 = -1
        # end of game?
        if reward:
            # terminal step -> game over
            qsa = 0
        else:
            # game not over
            # no need to compute qsa if alpha=0 (no training)
            if self.ALPHA and candidates:
                action1,_,allq1 = policy.play(state)
            if action1<0:
                qsa = 0
            else:
                qsa = allq1[0,action1]
        # update q(state0,action) if training is active
        if self.ALPHA and action!=-1:
            old = allq0[0,action]
            tde = reward + qsa - old
            new = old + self.ALPHA * tde
            policy.q.set(state0.inputs(), action, new, allq0)
        else:
            tde = 0
        self.sum_td_error += math.fabs(tde)
        self.count_td_error += 1
        # log transition
        log.debug('transition: %s --|%d|-> %s', state0, action, state)
        return state, action1


class AlgoPlay(Algo):

    def update(self, policy, state, action):
        state0 = copy.deepcopy(state)
        action,_,_ = policy.play(state)
        state,_ = state.transition(action)
        # log transition
        log.debug('transition: %s --|%d|-> %s', state0, action, state)
        return state, -1
