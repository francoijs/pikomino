#!/usr/bin/python
# pylint: disable=multiple-imports

import time, signal, argparse, logging
import episode
import state as piko_state
from algo import set_params, algo_sarsa, algo_qlearning, get_stats, reset_stats


DEFAULT_EPISODES    = 10000
DEFAULT_STEP        = 100
DEFAULT_ALPHA       = .3
DEFAULT_EPSILON     = .1
DEFAULT_LAYERS      = 3
DEFAULT_TEMPERATURE = 0
running = True

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger('main')


def stop(_signum, _frame):
    log.info('stopping...')
    global running
    running = False

def train(parser, Episode, State):
    # sigterm
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    # parse args
    parser.add_argument('--episodes', '-e', metavar='N', type=int, default=DEFAULT_EPISODES,
                        help='total number of episodes (default=%d)'%(DEFAULT_EPISODES))
    parser.add_argument('--step', '-s', metavar='S', type=int, default=DEFAULT_STEP,
                        help='number of episodes per step (default=%d)'%(DEFAULT_STEP))
    parser.add_argument('--offset', metavar='O', type=int, default=0,
                        help='offset in count of episodes (default=0)')
    parser.add_argument('--hash', action='store_true',
                        help='use hash table instead of NN')
    parser.add_argument('--base', '-b', metavar='DIR', type=str, default=None,
                        help='base directory for models backup')
    parser.add_argument('--sarsa', metavar='DECAY', type=int, default=0,
                        help='use algo sarsa with decaying exploration ratio (default=off)')
    parser.add_argument('--alpha', metavar='ALPHA', type=float, default=DEFAULT_ALPHA,
                        help='learning rate (default=%.3f)'%(DEFAULT_ALPHA))
    parser.add_argument('--decay', metavar='K', type=int, default=0,
                        help='learning rate decay (default=off)')
    parser.add_argument('--epsilon', metavar='EPSILON', type=float, default=DEFAULT_EPSILON,
                        help='exploration ratio (default=%.3f)'%(DEFAULT_EPSILON))
    parser.add_argument('--softmax', metavar='T', type=float, default=0,
                        help='use a softmax exploration strategy with temperature T (default=off)')
    parser.add_argument('--layers', '-l', metavar='L', type=int, default=DEFAULT_LAYERS,
                        help='number of hidden layers (default=%d)'%(DEFAULT_LAYERS))
    parser.add_argument('--width', '-w', metavar='W', type=int, default=0,
                        help='width of hidden layers (default=same as input layer)')
    parser.add_argument('--debug', '-d', action='store_true', default=False, 
                        help='display debug log')
    args = parser.parse_args()
    log.debug(args)
    # base directory
    if not args.base:
        args.base = ''
    elif args.base[-1] != '/':
        args.base += '/'
    # params of training
    EPISODES = args.episodes
    STEP     = args.step
    # algo
    if args.sarsa > 0:
        algo = algo_sarsa
    else:
        algo = algo_qlearning
    # learning mode
    set_params(args.alpha, args.epsilon, args.softmax, debug=args.debug)
    alpha = args.alpha
    epsilon = args.epsilon
    if args.hash:
        from q_hash import StrategyHashQ
        q = StrategyHashQ(args.base+Episode.dbname)
    else:
        from q_network import NetworkQ
        q = NetworkQ(args.base+Episode.dbname, State, layers=args.layers, width=args.width)
    # counters
    won = episodes = rate = tot_turns = tot_rounds = 0
    reset_stats()
    Episode.reset_stats()
    time0 = time.time()
    while running:
        state,turns,rounds = Episode.episode(q, algo=algo)
        if state.player_wins():
            won += 1
        episodes += 1
        tot_turns += turns
        tot_rounds += rounds
        if not episodes % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            # RL stats
            mean_td_error, mean_ps = get_stats()
            log.info('games: %d / won: %.1f%% of last %d / turns: %.1f/episode\n'
                     'time: %.2fms/episode / mean td error: %.3f / mean softmax prob: %.2f\n'
                     '%s',
                     episodes, rate, STEP, float(tot_turns)/STEP,
                     perf, mean_td_error, mean_ps,
                     Episode.print_stats())
            won = tot_turns = tot_rounds = 0
            reset_stats()
            Episode.reset_stats()
            q.save(epoch=(episodes+args.offset))
            if args.decay:
                # adjust learning rate with decay
                alpha = args.alpha * args.decay / (args.decay+episodes+args.offset)
                log.info('learning rate: %.3f', alpha)
            if args.sarsa > 0:
                # sarsa: adjust exploration rate
                epsilon = args.epsilon * args.sarsa / (args.sarsa+episodes+args.offset)
                log.info('exploration rate: %.3f', epsilon)
            set_params(alpha, epsilon, args.softmax, debug=args.debug)
            time0 = time.time()
        if episodes == EPISODES:
            break    
    q.save()

    
if __name__ == "__main__":
    train(argparse.ArgumentParser(description='Train the strategy.'), episode.EpisodePiko, piko_state.State)
