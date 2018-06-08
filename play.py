#!/usr/bin/python

import sys, argparse, copy
import strategy
from q_network import StrategyNetworkQ
from state import State


DBNAME = 'strategy'
DEFAULT_LAYERS = 3

def main(argv=sys.argv):
    # parse args
    parser = argparse.ArgumentParser(description='Play a game.')
    parser.add_argument('--hash', action='store_true',
                        help='use hash table instead of NN')
    parser.add_argument('--layers', '-l', metavar='L', type=int, default=DEFAULT_LAYERS,
                        help='number of hidden layers (default=%d)'%(DEFAULT_LAYERS))
    args = parser.parse_args()
    print str(args)
    # playing mode
    strategy.s_setparams(0, 0, debug=True)
    q = StrategyNetworkQ(DBNAME, layers=args.layers)
    # initial state
    ai_state = State()
    # start game
    while True:

        # my turn
        print 'your turn:'
        my_state = ai_state.change_turn()
        while True:
            prev_state = copy.deepcopy(my_state)
            print 'state: %s / total: %d' % (my_state, my_state.total())
            candidates = my_state.find_candidates()
            if not candidates:
                # update state
                my_state.lose_tile()
                break
            action = -1
            while action not in candidates:
                try:
                    action = input('choose action %s: ' % (candidates))
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    action = -1
            my_state = my_state.transition(action)
            if action>5:
                break
        # print report for the round
        report('you', my_state.player, prev_state)
        if not my_state.stash:
            end_game(my_state)
            return 0

        # AI turn
        print 'AI turn:'
        ai_state = my_state.change_turn()
        while True:
            prev_state = copy.deepcopy(ai_state)
            action,_ = strategy.policy(ai_state, q)
            ai_state = ai_state.transition(action)
            print 'transition:', prev_state, '--|%d|->' % (action), ai_state
            if ai_state.end_of_turn():
                break
        # print report for the round
        report('AI', ai_state.player, prev_state)
        if not ai_state.stash:
            end_game(ai_state.change_turn())
            return 0

def report(id, mine_now, state_before):
    if mine_now:
        tile = mine_now[-1]
        if state_before.opponent and mine_now[-1]==state_before.opponent[-1]:
            print id+' steal tile', tile
            return
        elif tile in state_before.stash:
            print id+' take tile', tile
            return
    print id+' lose one tile'        

def end_game(state):
    my = state.player_score()
    her = state.opponent_score()
    if her>my:
        print 'you lose %d/%d' % (her, my)
    elif my>her:
        print 'you win %d/%d' % (my, her)
    else:
        print 'draw %d/%d' % (my, her)


if __name__ == "__main__":
    main()
