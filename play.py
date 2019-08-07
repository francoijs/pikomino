#!/usr/bin/env python3

import sys, argparse, copy, random, logging
from state import State
from policy import Policy

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger('main')


def main(argv=sys.argv):
    # parse args
    parser = argparse.ArgumentParser(description='Play a game.')
    parser.add_argument('model', metavar='MODEL', type=str,
                        help='model file')
    parser.add_argument('--game', '-g', metavar='GAME', type=str, default='piko',
                        help='name of game (default=piko)')
    parser.add_argument('--random', action='store_true', default=False,
                        help='play against random policy')
    parser.add_argument('--debug', '-d', action='store_true', default=False, 
                        help='display debug log')
    args = parser.parse_args()
    print(str(args))
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    # playing mode
    if args.random:
        policy = Policy.create('random')
    else:
        state = State.create(args.game)
        if args.model.endswith('.db'):
            from q_hash import HashQ
            q = HashQ(args.model, state.OUTPUTS)
        else:
            from q_network import NetworkQ
            q = NetworkQ(args.model)
        policy = Policy.create('exploit', q)
    # initial state
    my_state = State.create(args.game, True)
    ai_state = State.create(args.game, False)
    
    # who starts?
    human_starts = random.choice([True, False])
    if human_starts:
        print('you begin')
    else:
        print('AI begins')
    
    # start game
    while True:

        if human_starts:
            # my turn
            print('your turn:')
            while True:
                prev_state = copy.deepcopy(my_state)
                print('state: %s' % (my_state,))
                candidates = my_state.find_candidates()
                if not candidates:
                    # update state
                    my_state = my_state.transition(-1)
                    break
                action = -1
                while action not in candidates:
                    try:
                        action = int(input('choose action %s: ' % (candidates)))
                    except KeyboardInterrupt:
                        sys.exit()
                    except:
                        action = -1
                my_state = my_state.transition(action)
                if my_state.end_of_turn():
                    break
            # print report for the round
            my_state.report('you', prev_state)
            if my_state.end_of_game():
                end_game(my_state)
                return 0
            ai_state = my_state.change_turn()
        else:
            human_starts = True    

        # AI turn
        print('AI turn:')
        while True:
            prev_state = copy.deepcopy(ai_state)
            action,_,_ = policy.play(ai_state)
            ai_state = ai_state.transition(action)
            print('transition: %s --|%d|-> %s' % (prev_state, action, ai_state))
            if ai_state.end_of_turn():
                break
        # print report for the round
        ai_state.report('AI', prev_state)
        if ai_state.end_of_game():
            end_game(ai_state.change_turn())
            return 0
        my_state = ai_state.change_turn()

def end_game(state):
    my = state.player_score()
    her = state.opponent_score()
    if her>my:
        print('you lose %d/%d' % (my, her))
    elif my>her:
        print('you win %d/%d' % (my, her))
    else:
        print('draw %d/%d' % (my, her))


if __name__ == "__main__":
    main()
