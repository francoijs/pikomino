#!/usr/bin/python

import sys
import strategy, piko

DBNAME = 'strategy.db'

def main(argv=sys.argv):
    # playing mode
    strategy.setparams(0, 0, log=True)
    piko.setparams(0, 0)
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
        print 'your turn:', my_state
        smallest = [tiles[0]]
        if opponent:
            smallest = smallest + [opponent[-1]]
        tile = my_roll(min(smallest))
        my_state = strategy.transition(my_state, tile)
        ai_state = (tiles, mine, strategy.score(mine), opponent, strategy.score(opponent))
        if tile<0:
            print 'you lose one tile'
        else:
            print 'you take tile', mine[-1]
        if not tiles:
            end_game(my_state)
            return 0
        # AI turn
        action = strategy.policy(ai_state, q)
        if action == 0:
            target = 0
        else:
            target = mine[-1]
            print 'AI is sniping your tile', target
        roll_state,_ = piko.episode(([0,0,0,0,0,0], piko.roll(8)), strategy.loadq(target))
        tile = piko.score(roll_state)
        num_tiles = len(opponent)
        ai_state = strategy.transition(ai_state, tile)
        my_state = (tiles, opponent, strategy.score(opponent), mine, strategy.score(mine))
        if len(opponent) > num_tiles:
            print 'AI takes tile', opponent[-1]
        else:
            print 'AI loses one tile'
        if not tiles:
            end_game(my_state)
            return 0

def end_game(state):
    if state[2] > state[4]:
        print 'you lose %d/%d' % (state[2], state[4])
    elif state[4] > state[2]:
        print 'you win %d/%d' % (state[4], state[2])
    else:
        print 'draw %d/%d' % (state[4], state[2])

def my_roll(smallest):
    dices = 8
    state = ([0,0,0,0,0,0], piko.roll(8))
    while True:
        print 'state: %s / total: %d' % (state, piko.total(state))
        candidates = piko.find_candidates(state, smallest)
        if not candidates:
            return -1
        action = -1
        while action not in candidates:
            try:
                action = input('choose action %s: ' % (candidates))
            except KeyboardInterrupt:
                sys.exit()
            except:
                action = -1
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
