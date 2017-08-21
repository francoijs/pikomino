#!/usr/bin/python

import random, copy, math, collections, os, time
import cPickle as pickle

DBNAME = 'q.db'
STEP = 10000

def main():
    q = loadq(DBNAME)
    # counters
    won = 0
    all = 0
    rate = 0
    time0 = time.time()
    while True:
        state,reward = episode(([0,0,0,0,0,0], roll(8), 21), q)
#        print 'end:',state,reward
        if reward > 0:
            won += 1
        all += 1
        if not all % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            print 'games: %d / won: %.1f%% of last %d / time: %.3fms/game' % (all, rate, STEP, perf)
            won = 0
            time0 = time.time()
        if all == 100000:
            break    
    saveq(DBNAME, q)

def episode(state, q):
    """ Run an episode and return final state and reward """
    while True:
        state0 = copy.deepcopy(state)
        action = policy(state, q)
        if action == -1:
            # roll is lost
            reward = -100
        elif action > 5:
            # keep some dices then stop
            state[0][action-6] += state[1][action-6]
            reward = score(state)
            if reward == state[2]:
                state[2] = min(state[2]+1, 36)
            state = (state[0], [0,0,0,0,0,0], state[2])
        else:
            # keep some dices then reroll
            state[0][action] += state[1][action]
            reward = 0
            state = (state[0], roll(8-sum(state[0])), state[2])
        # update q(state0,action)
        old = getq(q, state0, action)
        new = old + 0.1 * ( reward + max([getq(q,state,a) for a in range(12)]) - old )
        setq(q, state0, action, new)
#        print state0, '--|%d|->' % (action), state
        if reward != 0:
            break
    return state,reward

def policy(state, q):
    """
    Return preferred action for the given state:
    a in [0-5] : keep dice value a and reroll
    a in [6-11]: keep dice value a-6 and stop
    """
    # dices that may be kept before rerolling
    candidates = [n for n in range(6) if state[1][n]>0 and state[0][n]==0]
    if score(state) >= state[2]:
        # dices that may be kept before stopping
        candidates += [6+n for n in range(6) if state[1][n]>0 and state[0][n]==0]
    if len(candidates) == 0:
        # no dice may be kept -> this roll is lost
        return -1
    if random.random() < 0.1:   # epsilon
        return random.choice(candidates)
    # return best action
    return candidates[ max(range(len(candidates)), key=lambda i: getq(q,state,candidates[i])) ]

def score(state):
    """ Return score for the given state """
    if state[0][0] == 0:
        return 0
    return 5*state[0][0] + sum([n*state[0][n] for n in range(6)])
    
def roll(n):
    """ Roll n dices and return 6-array with count for each value """
    roll = [0,0,0,0,0,0]
    draw = [random.randint(0,5) for _ in range(n)]
    for d in draw:
        roll[d] += 1
    return roll

def _hash(state, action):
    return hash( (tuple(state[0]), tuple(state[1]), state[2], action) )
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

    
if __name__ == "__main__":
    main()
