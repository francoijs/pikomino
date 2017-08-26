#!/usr/bin/python

import sys
import strategy, piko

DBNAME = 'strategy.db'

def main(argv=sys.argv):
    # playing mode
    strategy.setparams(0, 0, log=True)
    q = piko.loadq(DBNAME)
    # game elements
    mine = []
    opponent = []
    tiles = strategy.sortedlist(range(21,37))
    my_state = (tiles, opponent, 0, mine, 0)
    ai_state = (tiles, mine, 0, opponent, 0)
    # start game
    while True:
        # my turn
        print my_state
        tile = my_roll()
        my_state = strategy.transition(my_state, tile)
        if tile<0:
            print 'you lose one tile'
        else:
            print 'you take tile', my_state[3][-1]

def my_roll():
    dices = 8
    state = ([0,0,0,0,0,0], piko.roll(8))
    while True:
        print 'state: %s / total: %d' % (state, piko.total(state))
        candidates = piko.find_candidates(state)
        if not candidates:
            return -1
        action = -1
        while action not in candidates:
            action = input('choose action %s: ' % (candidates))
        if action>5:
            # keep some dices then stop
            state[0][action-6] += state[1][action-6]
            return piko.score(state)
        else:
            # keep some dices then reroll
            state[0][action] += state[1][action]
            state = (state[0], piko.roll(8-sum(state[0])))


if __name__ == "__main__":
    main()
