import copy, random, bisect
import numpy as np
from q_hash import HashQ
from state import State


LOG = False
ALPHA = 0.3    # learning rate
EPSILON = 0.1


def s_setparams(alpha, epsilon, log=False):
    global ALPHA, EPSILON, LOG
    ALPHA = alpha
    EPSILON = epsilon
    print 'strategy: alpha=%.1f / epsilon=%.1f' % (ALPHA, EPSILON)
    LOG = log

def episode(q):
    """ Run an episode and return final state, reward, my score """
    # initial state
    state = State()
    my_turn = True
    while True:
        state0 = copy.deepcopy(state)
        action,candidates = policy(state, q)
        if LOG:
            print 'candidates:', state, ':', candidates
        state = state.transition(action)
        # end of game?
        if not state.stash:
            # no more tiles in stash
            if (my_turn and state.player_wins()):
                qsa = reward = 1    # win
            else:
                qsa = reward = -1   # loss or draw
        else:
            # game not over
            reward = 0
            if candidates:
                qsa = max([q.get(state.inputs(),a) for a in candidates])
            else:
                qsa = 0
        # update q(state0,action)
        old = q.get(state0.inputs(), action)
        new = old + ALPHA * ( reward + qsa - old )
        q.set(state0.inputs(), action, new)
        # log transition
        if LOG:
            print 'transition:', state0, '--|%d|->' % (action), state
        if reward:
            # game is over
            break
        # change player?
        if state.end_of_turn():
            state = state.change_turn()
            my_turn = not my_turn
    return reward, (state.player_score() if my_turn else state.opponent_score())

def policy(state, q):
    """
    Return preferred action for the given state:
    - a in [0-5] : keep dice value a and reroll
    - a in [6-11]: keep dice value a-6 and stop
    - a = -1: no possible action
    """
    candidates = state.find_candidates()
    if len(candidates) == 0:
        # no dice available -> this roll is lost
        action = -1
    elif random.random() < EPSILON:
        # exploration
        action = random.choice(candidates)
    else:
        # return best action
        allQ = q.get_all(state.inputs())
        action = candidates[ max(range(len(candidates)), key=lambda i: allQ[0,candidates[i]]) ]
    return action, candidates
