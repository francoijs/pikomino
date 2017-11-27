import random, copy, math, collections, os, time


ALPHA = 0.3    # learning rate
EPSILON = 0.1
LOG = False
TARGET = 0     # target tile (0 for the largest possible)

def setparams(alpha, epsilon, log=False, target=0):
    global ALPHA, EPSILON, LOG, TARGET
    ALPHA = alpha
    EPSILON = epsilon
    print 'roll: alpha=%.3f / epsilon=%.3f' % (ALPHA, EPSILON)
    LOG = log
    TARGET = target

def episode(state, q):
    """ Run an episode and return final state and reward """
    # eligibility traces for this episode (no decay)
    traces = []
    while True:
        state0 = copy.deepcopy(state)
        action = policy(state, q)
        state, reward, qsa = transition(state, action, q)
        old = q.get(state0, action)
        new = old + ALPHA * ( reward + qsa - old )
        q.set(state0, action, new)
        if LOG:
            print state0, '--|%d|->' % (action), state
        if reward != 0:
            break
    return state,reward

def policy(state, q):
    """
    Return preferred action for the given state:
    - a in [0-5] : keep dice value a and reroll
    - a in [6-11]: keep dice value a-6 and stop
    """
    candidates = find_candidates(state)
    if len(candidates) == 0:
        # no dice available -> this roll is lost
        return -1
    if random.random() < EPSILON:
        # exploration
        return random.choice(candidates)
    # return best action
    return candidates[ max(range(len(candidates)), key=lambda i: q.get(state,candidates[i])) ]

def find_candidates(state, opp=0):
    """ Return list of candidates actions """
    assert sum(state[0]) + sum(state[1]) == 8
    # dices that may be kept before rerolling
    candidates = [n for n in range(6) if state[1][n]>0 and state[0][n]==0]
    # dices that may be kept before stopping
    stop = []
    for action in candidates:
        if action==0:
            new_score = total(state) + state[1][0]*5
            if new_score >= state[2]:
                stop.append(6)
        else:
            # cannot stop if score not at least bigger than the smallest available tile
            # FIXME: if the opponent tile is smaller that the smallest from stash,
            # it may be not allowed to stop -> fix this case
            new_score = total(state) + state[1][action]*action
            if state[0][0] and (new_score>=state[2] or new_score==opp):
                stop.append(6+action)
    return candidates + stop

def transition(state, action, q):
    if action == -1:
        # roll is lost
        qsa = reward = -100
    elif action > 5:
        # keep some dices then stop
        state[0][action-6] += state[1][action-6]
        tile = score(state)
        if TARGET == 0:
            qsa = reward = score(state)
        elif tile == TARGET:
            qsa = reward = 100
        else:
            qsa = reward = -100
            state = (state[0], [0,0,0,0,0,0])
    else:
        # keep some dices then reroll
        state[0][action] += state[1][action]
        reward = 0
        state = (state[0], roll(8-sum(state[0])), state[2])
        candidates = find_candidates(state)
        if candidates:
            qsa = max([q.get(state,a) for a in candidates])
        else:
            qsa = 0
    return state, reward, qsa

def total(state):
    return 5*state[0][0] + sum([n*state[0][n] for n in range(6)])
    
def score(state):
    """ Return score for the given state """
    if state[0][0] == 0:
        return -100
    tile = total(state)
    if tile > 20:
        return tile
    return -100
    
def roll(n):
    """ Roll n dices and return 6-array with count for each value """
    roll = [0,0,0,0,0,0]
    draw = [random.randint(0,5) for _ in range(n)]
    for d in draw:
        roll[d] += 1
    return roll
