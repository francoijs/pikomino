import copy, random, bisect, logging
import numpy as np
from state import State


ALPHA = 0.3    # learning rate
EPSILON = 0.1

log = logging.getLogger('episode')


def s_setparams(alpha, epsilon, debug=False):
    global ALPHA, EPSILON
    ALPHA = alpha
    EPSILON = epsilon
    log.debug('strategy: alpha=%.1f / epsilon=%.1f', ALPHA, EPSILON)
    if debug:
        log.setLevel(logging.DEBUG)

def algo_qlearning(q, state, action):
    state0 = copy.deepcopy(state)
    action0,candidates,allq0 = policy(state, q)
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
            allq = q.get_all(state.inputs())
            qsa = max([allq[0,a] for a in candidates])
        else:
            qsa = 0
    # update q(state0,action) if training is active
    if ALPHA and action!=-1:
        old = allq0[0,action]
        new = old + ALPHA * ( reward + qsa - old )
        q.set(state0.inputs(), action, new, allq0)
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, -1

def algo_sarsa(q, state, action):
    state0 = copy.deepcopy(state)
    action0,candidates,allq0 = policy(state, q)
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
            action1,_,allq1 = policy(state, q)
        if action1<0:
            qsa = 0
        else:
            qsa = allq1[0,action1]
    # update q(state0,action) if training is active
    if ALPHA and action!=-1:
        old = allq0[0,action]
        new = old + ALPHA * ( reward + qsa - old )
        q.set(state0.inputs(), action, new, allq0)
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, action1

def episode(q_player, q_opponent=None, algo=algo_qlearning):
    """ Run an episode and return final state. """
    # DQN of opponent
    if not q_opponent:
        q_opponent = q_player
    # initial state & action
    state = State()
    action = -1
    my_turn = True
    # number of steal
    rounds = steal = opp_top_tile = 0
    while True:
        if my_turn:
            q = q_player
        else:
            q = q_opponent
        state,action = algo(q, state, action)
        if state.end_of_game():
            # game is over
            break
        # change player?
        if state.end_of_turn():
            rounds += 1
            if state.player and state.player[-1]==opp_top_tile:
                steal += 1
            if state.player:
                opp_top_tile = state.player[-1]
            else:
                opp_top_tile = 0
            state = state.change_turn()
            action = -1
            my_turn = not my_turn
    return (state if my_turn else state.change_turn()), steal, rounds

def policy(state, q):
    """
    Return preferred action for the given state:
    - a in [0-5] : keep dice value a and reroll
    - a in [6-11]: keep dice value a-6 and stop
    - a = -1: no possible action
    """
    candidates = state.find_candidates()
    log.debug('candidates for %s: %s', state, candidates)    
    if len(candidates) == 0:
        # no dice available -> this roll is lost
        return -1, [], np.empty((0,0))
    allQ = q.get_all(state.inputs())
    if random.random() < EPSILON:
        # exploration
        action = random.choice(candidates)
    else:
        # return best action
        action = candidates[ max(range(len(candidates)), key=lambda i: allQ[0,candidates[i]]) ]
    return action, candidates, allQ
