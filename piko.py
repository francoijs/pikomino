#!/usr/bin/python

import random, copy, math

def main():
    state = ([0,0,0,0,0,0], roll(8), 21)
    state,reward = episode(state)
    print 'end:',state,reward

def episode(state):
    while True:
        state0 = copy.deepcopy(state)
        action = policy(state)
        if action == -1:
            # roll is lost
            reward = -100
            break
        if action > 5:
            # keep some dices then stop
            state[0][action-6] += state[1][action-6]
            reward = score(state)
            break
        # keep some dices then reroll
        state[0][action] += state[1][action]
        state = (state[0], roll(8-sum(state[0])), state[2])
        print state0, '->', state
    return state,reward

def policy(state):
    # dices that may be kept before rerolling
    candidates = [n for n in range(6) if state[1][n]>0 and state[0][n]==0]
    if score(state) >= state[2]:
        # dices that may be kept before stopping
        candidates += [6+n for n in range(6) if state[1][n]>0 and state[0][n]==0]
    if len(candidates) == 0:
        # no dice may be kept -> this roll is lost
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

if __name__ == "__main__":
    main()
