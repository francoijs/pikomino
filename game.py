#!/usr/bin/env python3

import logging, argparse, signal
from episode import EpisodePiko
from algo import AlgoPlay
from policy import PolicyExploit


DEFAULT_GAMES=1
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
)
log = logging.getLogger('main')
running = True

def match(p1, p2, games):
    # game on
    log.info('playing <%s> against <%s>...', p1.q.fname, 'itself' if p1==p2 else p2.q.fname)
    wins_left = wins_right = draws = played = 0
    for game in range(games):
        state,_,rounds = EpisodePiko.episode(p1, p2, algo=AlgoPlay())
        log.info('game %d: rounds=%3d, winner=%s, score=%d/%d',
                 game, rounds,
                 'left' if state.player_wins() else 'right' if state.opponent_wins() else 'draw',
                 state.player_score(), state.opponent_score()
        )
        played += 1
        if state.player_wins():
            wins_left += 1
        elif state.opponent_wins():
            wins_right += 1
        else:
            draws += 1
        if not running:
            break
    log.info('stats: left %d%% / right %d%% / draw %d%%',
             wins_left*100/played,
             wins_right*100/played,
             draws*100/played
    )
    return 1 if wins_left > wins_right else -1


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Play matches to determine the best model between N.')
    parser.add_argument('models', metavar='MODEL', type=str, nargs='+',
                        help='model files (at least 2)')
    parser.add_argument('--games', '-g', metavar='G', type=int, default=DEFAULT_GAMES,
                        help='number of games to play between 2 models (default=%d)'%(DEFAULT_GAMES))
    parser.add_argument('--jy', action='store_true', default=False,
                        help='play the MODEL against the model of <picomino_play>')
    parser.add_argument('--debug', '-d', action='store_true', default=False, 
                        help='display debug log')
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    log.debug(args)

    if args.jy:
        # play against JY model
        from q_network import NetworkQ
        from policy_jy import PolicyJY
        policy = PolicyExploit(NetworkQ(args.models[0]))
        jy_pol = PolicyJY()
        best = policy
        if match(policy, jy_pol, args.games) < 0:
            best = jy_pol
        log.info('winner is %s', best.name)

    else:
        # match models against each other
        Q = {}
        def compare(f1, f2):
            from q_network import NetworkQ
            if f1 not in Q:
                Q[f1] = NetworkQ(f1)
            if f2 not in Q:
                Q[f2] = NetworkQ(f2)
            return match(PolicyExploit(Q[f1]), PolicyExploit(Q[f2]), args.games)
        best = args.models[0]
        for key in args.models[1:]:
            if not running:
                break
            if compare(best, key) < 0:
                best = key
        log.info('winner is %s', best)


def stop(_signum, _frame):
    log.info('stopping...')
    global running
    running = False
    
if __name__ == "__main__":
    # sigterm
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    main()
