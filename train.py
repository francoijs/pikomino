#!/usr/bin/python
# pylint: disable=multiple-imports

import time, signal, argparse, logging
from episode import episode, s_setparams, algo_sarsa, algo_qlearning


DBNAME = 'strategy'
DEFAULT_EPISODES = 100000
DEFAULT_STEP     = 1000
DEFAULT_ALPHA    = .3
DEFAULT_EPSILON  = .1
DEFAULT_LAYERS   = 3
running = True

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger('main')


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Train the strategy.')
    parser.add_argument('--episodes', '-e', metavar='N', type=int, default=DEFAULT_EPISODES,
                        help='total number of episodes (default=%d)'%(DEFAULT_EPISODES))
    parser.add_argument('--step', '-s', metavar='S', type=int, default=DEFAULT_STEP,
                        help='number of episodes per step (default=%d)'%(DEFAULT_STEP))
    parser.add_argument('--offset', metavar='O', type=int, default=0,
                        help='offset in count of episodes (default=0)')
    parser.add_argument('--hash', action='store_true',
                        help='use hash table instead of NN')
    parser.add_argument('--algo', metavar='ALGO', type=str, default='q-learning',
                        help='algo (q-learning or sarsa)')
    parser.add_argument('--alpha', metavar='ALPHA', type=float, default=DEFAULT_ALPHA,
                        help='learning rate (default=%.3f)'%(DEFAULT_ALPHA))
    parser.add_argument('--epsilon', metavar='EPSILON', type=float, default=DEFAULT_EPSILON,
                        help='exploration ratio (default=%.3f)'%(DEFAULT_EPSILON))
    parser.add_argument('--layers', '-l', metavar='L', type=int, default=DEFAULT_LAYERS,
                        help='number of hidden layers (default=%d)'%(DEFAULT_LAYERS))
    parser.add_argument('--decay', metavar='K', type=int, default=0,
                        help='learning rate decay (default=off)')
    parser.add_argument('--debug', '-d', action='store_true', default=False, 
                        help='display debug log')
    args = parser.parse_args()
    log.debug(args)
    # params of training
    EPISODES = args.episodes
    STEP     = args.step
    # algo
    if args.algo == 'sarsa':
        algo = algo_sarsa
    else:
        algo = algo_qlearning
    # learning mode
    s_setparams(args.alpha, args.epsilon, debug=args.debug)
    if args.hash:
        from q_hash import StrategyHashQ
        q = StrategyHashQ(DBNAME)
    else:
        from q_network import StrategyNetworkQ
        q = StrategyNetworkQ(DBNAME, layers=args.layers)
    # counters
    won = episodes = rate = tot_score = mark = tot_mark = tot_null = tot_turns = tot_rounds = sum_td_error = 0
    time0 = time.time()
    while running:
        state,mark,turns,rounds,stde = episode(q, algo=algo)
        if state.player_wins():
            won += 1
            tot_score += state.player_score()
        episodes += 1
        tot_mark += mark
        tot_turns += turns
        tot_rounds += rounds
        sum_td_error += stde
        if state.player_score()==0:
            tot_null += 1
        if not episodes % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            null_rate = 100 * float(tot_null)/STEP
            avg_mark = float(tot_mark)/STEP
            if won:
                avg_score = float(tot_score)/won
            else:
                avg_score = 0
            log.info('games: %d / won: %.1f%% of last %d / turns: %.1f/game / null: %.1f%% / avg score: %.1f / avg mark: %.1f%% / time: %.3fms/game / mean td error: %.3f',
                     episodes, rate, STEP, float(tot_turns)/STEP, null_rate, avg_score, avg_mark, perf, float(sum_td_error)/tot_rounds)
            won = tot_null = tot_score = tot_mark = tot_turns = tot_rounds = sum_td_error = 0
            q.save(epoch=(episodes+args.offset))
            if args.decay:
                # adjust learning rate with decay
                alpha = args.alpha * args.decay / (args.decay+episodes+args.offset)
                s_setparams(alpha, args.epsilon, debug=args.debug)
                log.info('learning rate: %.3f', alpha)
            time0 = time.time()
        if episodes == EPISODES:
            break    
    q.save()

def stop(_signum, _frame):
    log.info('stopping...')
    global running
    running = False
    
if __name__ == "__main__":
    # sigterm
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    main()
