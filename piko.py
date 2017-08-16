#!/usr/bin/python

import random, copy

def main():
    state = ([0,0,0,0,0,0], roll(8))
    state,reward = episode(state)
    print 'end:',state,reward

def episode(state):
    while True:
        state0 = copy.deepcopy(state)
        action = policy(state)
        if action == -1:
            # no action available
            reward = -100
            break
        if action == 6:
            # action = 'stop'
            reward = score(state)
            break
        state = play(state, action)
        print state0, '->', state
    return state,reward

def policy(state):
    candidates = [n for n in range(6) if state[1][n]>0 and state[0][n]==0]
    if score(state)>20:
        candidates += [6]
    if len(candidates) == 0:
        return -1
    return random.choice(candidates)

def score(state):
    if state[0][0] == 0:
        return 0
    return 5*state[0][0] + sum([n*state[0][n] for n in range(6)])
    
def roll(n):
    roll = [0,0,0,0,0,0]
    draw = [random.randint(0,5) for _ in range(n)]
    for d in draw:
        roll[d] += 1
    return roll

def play(state, action):
    if action is 6:
        return state, score(state)
    state[0][action] += state[1][action]
    return (state[0], roll(8-sum(state[0])))

if __name__ == "__main__":
    main()
