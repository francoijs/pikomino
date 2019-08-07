#!/usr/bin/env python3

import logging, argparse, signal, re, random
from episode import Episode
from algo import AlgoPlay
from policy import PolicyExploit
from state import State


DEFAULT_GAMES=1
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
)
log = logging.getLogger('main')
running = True

def match(p1, p2, games, gname):
    # game on
    log.info('playing <%s> against <%s>...', p1.q.fname, 'itself' if p1==p2 else p2.q.fname)
    wins_left = wins_right = draws = played = 0
    for game in range(games):
        left_starts = random.choice([True, False])
        state,_,rounds = Episode(AlgoPlay(), p1, p2).run(State.create(gname, left_starts))
        log.info('game %d: 1st=%s, rounds=%3d, winner=%s, score=%d/%d',
                 game, 'left ' if left_starts else 'right', rounds,
                 'left ' if state.player_wins() else 'right' if state.opponent_wins() else 'draw',
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
    return 1 if wins_left > wins_right else 0 if wins_left == wins_right else -1


def load(fname, outputs):
    if re.match('.*\.db[\-0-9]*', fname):
        from q_hash import HashQ
        return HashQ(fname, outputs)
    elif re.match('.*\.h5[\-0-9]*', fname):
        from q_network import NetworkQ
        return NetworkQ(fname)
    else:
        raise Exception('filename pattern not recognized: ' + fname)

    
def main():
    # parse args
    parser = argparse.ArgumentParser(description='Play matches to determine the best model between N.')
    parser.add_argument('models', metavar='MODEL', type=str, nargs='+',
                        help='model files (at least 2)')
    parser.add_argument('--games', '-g', metavar='G', type=int, default=DEFAULT_GAMES,
                        help='number of games to play between 2 models (default=%d)'%(DEFAULT_GAMES))
    parser.add_argument('--game', metavar='GAME', type=str, default='piko',
                        help='name of game (default=piko)')
    parser.add_argument('--jy', action='store_true', default=False,
                        help='play the MODEL against the model of <picomino_play>')
    parser.add_argument('--debug', '-d', action='store_true', default=False, 
                        help='display debug log')
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    log.debug(args)

    # number of actions
    outputs = State.create(args.game).OUTPUTS

    if args.jy:
        # play against JY model
        from policy_jy import PolicyJY
        policy = PolicyExploit(load(args.models[0], outputs))
        jy_pol = PolicyJY()
        best = policy
        if match(policy, jy_pol, args.games, args.game) < 0:
            best = jy_pol
        log.info('winner is %s', best.name)

    else:
        # match models against each other
        Q = {}
        def compare(f1, f2):
            if f1 not in Q:
                Q[f1] = load(f1, outputs)
            if f2 not in Q:
                Q[f2] = load(f2, outputs)
            return match(PolicyExploit(Q[f1]), PolicyExploit(Q[f2]), args.games, args.game)
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
