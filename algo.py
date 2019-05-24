import copy, logging, random, math
import numpy as np
from policy import PolicyEGreedy, PolicySoftmax


log = logging.getLogger('algo')

# TODO: move to new static class AlgoQLearning
ALPHA       = 0.3    # learning rate

def set_params(alpha, debug=False):
    global ALPHA
    ALPHA = alpha
    log.debug('algo: alpha=%.2f', ALPHA)
    if debug:
        log.setLevel(logging.DEBUG)

# stats
# TODO: move to new static class AlgoQLearning
sum_td_error = 0
count_td_error = 0

def get_stats():
    global sum_td_error, count_td_error
    return float(sum_td_error)/count_td_error if count_td_error else 0

def reset_stats():
    global sum_td_error, count_td_error
    sum_td_error = count_td_error = 0

def algo_qlearning(policy, state, action):
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
        if ALPHA and candidates:
            allq = policy.q.get_all(state.inputs())
            qsa = max([allq[0,a] for a in candidates])
        else:
            qsa = 0
    # update q(state0,action) if training is active
    if ALPHA and action!=-1:
        old = allq0[0,action]
        tde = reward + qsa - old
        new = old + ALPHA * tde
        policy.q.set(state0.inputs(), action, new, allq0)
    else:
        tde = 0
    global sum_td_error, count_td_error
    sum_td_error += math.fabs(tde)
    count_td_error += 1
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, -1

def algo_sarsa(policy, state, action):
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
        if ALPHA and candidates:
            action1,_,allq1 = policy.play(state)
        if action1<0:
            qsa = 0
        else:
            qsa = allq1[0,action1]
    # update q(state0,action) if training is active
    if ALPHA and action!=-1:
        old = allq0[0,action]
        tde = reward + qsa - old
        new = old + ALPHA * tde
        policy.q.set(state0.inputs(), action, new, allq0)
    else:
        tde = 0
    global sum_td_error, count_td_error
    sum_td_error += math.fabs(tde)
    count_td_error += 1
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, action1

def algo_play(policy, state, action):
    state0 = copy.deepcopy(state)
    action,_,_ = policy.play(state)
    state,_ = state.transition(action)
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, -1
