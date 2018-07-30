import copy, random, bisect, logging, math
import numpy as np
from state import State


ALPHA       = 0.3    # learning rate
EPSILON     = 0.1    # exploration ration
TEMPERATURE = 0      # softmax temperature

log = logging.getLogger('episode')

# softmax stats
sum_max_ps = 0
count_ps = 0


def setparams(alpha, epsilon, temperature, debug=False):
    global ALPHA, EPSILON, TEMPERATURE
    ALPHA = alpha
    EPSILON = epsilon
    TEMPERATURE = temperature
    log.debug('episode: alpha=%.2f / epsilon=%.2f / temperature=%.2f', ALPHA, EPSILON, TEMPERATURE)
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
        tde = reward + qsa - old
        new = old + ALPHA * tde
        q.set(state0.inputs(), action, new, allq0)
    else:
        tde = 0
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, -1, tde

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
        tde = reward + qsa - old
        new = old + ALPHA * tde
        q.set(state0.inputs(), action, new, allq0)
    else:
        tde = 0
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, action1, tde

def algo_play(q, state, action):
    state0 = copy.deepcopy(state)
    action,_,_ = policy(state, q)
    state,_ = state.transition(action)
    # log transition
    log.debug('transition: %s --|%d|-> %s', state0, action, state)
    return state, -1, 0

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
    turns = rounds = steal = opp_top_tile = sum_td_error = 0
    global count_ps, sum_max_ps
    count_ps = sum_max_ps = 0
    while True:
        if my_turn:
            q = q_player
        else:
            q = q_opponent
        state,action,td_error = algo(q, state, action)
        sum_td_error += math.fabs(td_error)
        rounds += 1
        if state.end_of_game():
            # game is over
            break
        # change player?
        if state.end_of_turn():
            turns += 1
            if state.player and state.player[-1]==opp_top_tile:
                steal += 1
            if state.player:
                opp_top_tile = state.player[-1]
            else:
                opp_top_tile = 0
            state = state.change_turn()
            action = -1
            my_turn = not my_turn
    return (state if my_turn else state.change_turn()), steal, turns, rounds, sum_td_error, float(sum_max_ps)/count_ps if count_ps else 0

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
    if TEMPERATURE > 0:
        # softmax distribution
        ps = np.zeros(len(candidates))
        idx = 0
        for c in candidates:
            ps[idx] = allQ[0,c]
            idx += 1
        action = np.random.choice(candidates, p=softmax(ps))
    elif random.random() < EPSILON:
        # e-greedy exploration
        action = random.choice(candidates)
    else:
        # exploitation: return best action
        action = candidates[ max(range(len(candidates)), key=lambda i: allQ[0,candidates[i]]) ]
    return action, candidates, allQ

def softmax(q_vector):
    """
    Return a softmax distribution of the values in q_vector.
    """
    q_vector = np.exp(q_vector / TEMPERATURE)
    q_vector /= np.sum(q_vector)
    # fix normalization
    q_vector[np.argmax(q_vector)] += 1-np.sum(q_vector)
    global sum_max_ps, count_ps
    sum_max_ps += max(q_vector)
    count_ps += 1
    return q_vector