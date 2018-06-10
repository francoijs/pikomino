#!/usr/bin/python

import logging, argparse
from strategy import episode, s_setparams


DEFAULT_GAMES=1
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
)
log = logging.getLogger('main')


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Play matches between 2 models.')
    parser.add_argument('model1', metavar='MODEL_1', type=str,
                        help='model file 1')
    parser.add_argument('model2', metavar='MODEL_2', type=str, nargs='?',
                        help='model file 2 (default=same as model 1)')
    parser.add_argument('--games', '-g', metavar='G', type=int, default=DEFAULT_GAMES,
                        help='number of games (default=%d)'%(DEFAULT_GAMES))
    parser.add_argument('--debug', '-d', action='store_true', default=False, 
                        help='display debug log')
    args = parser.parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)
    log.debug(args)
    
    # playing mode
    s_setparams(0, 0, debug=args.debug)

    # load DQN
    from q_network import StrategyNetworkQ
    q1 = StrategyNetworkQ(args.model1)
    if args.model2:
        q2 = StrategyNetworkQ(args.model2)
    else:
        q2 = q1

    # game on
    log.info('playing <%s> against <%s>...', q1.fname, 'itself' if q1==q2 else q2.fname)
    wins_left = wins_right = draws = 0
    for game in range(args.games):
        reward,state,_,rounds = episode(q1, q2)
        log.info('game %d: rounds=%3d, winner=%s, score=%d/%d',
                 game, rounds,
                 'left' if state.player_wins() else 'right' if state.opponent_wins() else 'draw',
                 state.player_score(), state.opponent_score()
        )
        if state.player_wins():
            wins_left += 1
        elif state.opponent_wins():
            wins_right += 1
        else:
            draws += 1
    log.info('stats: left %d%% / right %d%% / draw %d%%',
             wins_left*100/args.games,
             wins_right*100/args.games,
             draws*100/args.games
    )

if __name__ == "__main__":
    main()
