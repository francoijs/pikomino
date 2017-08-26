import random, copy, math, collections, os, time
import cPickle as pickle

ALPHA = 0.3    # learning rate
EPSILON = 0.1
LOG = False
TARGET = 0     # target tile (0 for the largest possible)

def setparams(alpha, epsilon, log=False, target=0):
    global ALPHA, EPSILON, LOG
    ALPHA = alpha
    EPSILON = epsilon
    LOG = log
    TARGET = target

def episode(state, q):
    """ Run an episode and return final state and reward """
    while True:
        state0 = copy.deepcopy(state)
        action = policy(state, q)
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
                qsa = reward = tile
            state = (state[0], [0,0,0,0,0,0])
        else:
            # keep some dices then reroll
            state[0][action] += state[1][action]
            reward = 0
            state = (state[0], roll(8-sum(state[0])))
            qsa = max([getq(q,state,a) for a in range(12)])
        # update q(state0,action)
        old = getq(q, state0, action)
        new = old + ALPHA * ( reward + qsa - old )
        setq(q, state0, action, new)
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
    return candidates[ max(range(len(candidates)), key=lambda i: getq(q,state,candidates[i])) ]

def find_candidates(state):
    """ Return list of candidates actions """
    # dices that may be kept before rerolling
    candidates = [n for n in range(6) if state[1][n]>0 and state[0][n]==0]
    # dices that may be kept before stopping
    stop = []
    for action in candidates:
        if action==0:
            new_score = total(state) + state[1][0]*5
            if new_score>20:
                stop.append(6)
        else:
            new_score = total(state) + state[1][action]*action
            if state[0][0] and new_score>20:
                stop.append(6+action)
    return candidates + stop

def transition(state0, action):
    state = copy.deepcopy(state0)
    state[0][action] += state[1][action]
    return state

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

def _hash(state, action):
    return hash( (tuple(state[0]), tuple(state[1]), action) )
    # h = 0
    # for b in state[0] + state[1] + [action]:
    #     h = (h<<4) + b
    # print h
    # return h
def getq(q, state, action):
    return q.get(_hash(state,action), 0)
def setq(q, state, action, val):
    q[_hash(state,action)] = val
    
def loadq(fname):
    if not os.path.isfile(fname):
        print 'creating empty db'
        q = {}
    else:
        with open(fname, 'rb') as file:
            q = pickle.load(file)
        print 'loaded %d q-values from' % (len(q)), fname
    return q
    
def saveq(fname, q):
    with open(fname, 'wb') as file:
        pickle.dump(q, file, pickle.HIGHEST_PROTOCOL)
    print '%d q-values saved to' % (len(q)), fname
