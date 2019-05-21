#!/usr/bin/python

import sys, argparse, copy, random
import algo
from q_network import NetworkQ
from state import State



def main(argv=sys.argv):
    # parse args
    parser = argparse.ArgumentParser(description='Play a game.')
    parser.add_argument('model', metavar='MODEL', type=str,
                        help='model file')
    args = parser.parse_args()
    print str(args)
    # playing mode
    algo.set_params(0, 0, 0, debug=True)
    q = NetworkQ(args.model, State=State)
    # initial state
    my_state = ai_state = State()

    # who starts?
    human_starts = random.choice([True, False])
    if human_starts:
        print 'you begin'
    else:
        print 'AI begins'
    
    # start game
    while True:

        if human_starts:
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
                my_state,_ = my_state.transition(action)
                if action>5:
                    break
            # print report for the round
            report('you', my_state.player, prev_state)
            if not my_state.stash:
                end_game(my_state)
                return 0
        else:
            human_starts = True    

        # AI turn
        print 'AI turn:'
        ai_state = my_state.change_turn()
        while True:
            prev_state = copy.deepcopy(ai_state)
            action,_,_ = algo.policy(ai_state, q)
            ai_state,_ = ai_state.transition(action)
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
