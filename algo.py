import copy, logging, random, math
import numpy as np

log = logging.getLogger('algo')


class Algo(object):
    
    ALPHA       = 0.3    # learning rate
    
    def set_params(self, alpha):
        self.ALPHA = alpha
        log.debug('algo: alpha=%.2f', self.ALPHA)


class AlgoQLearning(Algo):

    def __init__(self, alpha=.3):
        self.ALPHA = alpha
        self.sum_td_error = 0
        self.count_td_error = 0

    def get_stats(self):
        if self.count_td_error:
            return float(self.sum_td_error)/self.count_td_error
        return 0

    def reset_stats(self):
        self.sum_td_error = self.count_td_error = 0

    def update(self, policy, state, action):
        state0 = copy.deepcopy(state)
        action0,candidates,allq0 = policy.play(state)
        if action == -1:
            action = action0
        state,reward = state.transition(action)
        # end of game?
        if reward:
            # terminal step -> game over
            qsa = 0
        else:
            # game not over
            # no need to compute qsa if alpha=0 (no training)
            if self.ALPHA and candidates:
                allq = policy.q.get_all(state.inputs())
                qsa = max([allq[0,a] for a in candidates])
            else:
                qsa = 0
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
        return state, -1



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
