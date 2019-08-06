#!/usr/bin/env python3
# pylint: disable=multiple-imports

import time, signal, argparse, logging, random
from episode import Episode
from state import State
from algo import AlgoSarsa, AlgoQLearning, AlgoPlay
from policy import Policy, PolicyExploit


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

def train(parser):
    # sigterm
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    # parse args
    parser.add_argument('--game', '-g', metavar='GAME', type=str, default='piko',
                        help='name of game (default=piko)')
    parser.add_argument('--episodes', '-e', metavar='N', type=int, default=DEFAULT_EPISODES,
                        help='total number of episodes (default=%d)'%(DEFAULT_EPISODES))
    parser.add_argument('--step', '-s', metavar='S', type=int, default=DEFAULT_STEP,
                        help='number of episodes per step (default=%d)'%(DEFAULT_STEP))
    parser.add_argument('--validation', '-v', metavar='V', type=int, default=0,
                        help='number of validation episodes run at each step (default=0)')
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
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    log.debug(args)
    # base directory
    if not args.base:
        args.base = ''
    elif args.base[-1] != '/':
        args.base += '/'
    # params of training
    EPISODES = args.episodes
    STEP     = args.step
    # q-store
    state = State.create(args.game)
    if args.hash:
        from q_hash import HashQ
        q = HashQ(args.base+args.game, state.OUTPUTS)
    else:
        from q_network import NetworkQ
        q = NetworkQ(args.base+args.game, state.INPUTS, state.OUTPUTS, layers=args.layers, width=args.width)
    # algo
    if args.sarsa > 0:
        algo = AlgoSarsa()
    else:
        algo = AlgoQLearning(q)
    # policy
    if args.softmax > 0:
        policy = Policy.create('softmax', q)
    else:
        policy = Policy.create('egreedy', q)
    # learning mode
    algo.set_params(args.alpha)
    policy.set_params(args.epsilon, args.softmax)
    alpha = args.alpha
    epsilon = args.epsilon
    # counters
    won = episodes = tot_turns = tot_backups = 0
    algo.reset_stats()
    policy.reset_stats()
    time0 = time.time()
    while running:
        # initial state
        state = State.create(args.game, random.choice([True, False]))
        state,turns,backups = Episode(algo, policy).run(state)
        episodes += 1
        if not args.validation:
            # no validation: update stats during training
            if state.player_wins():
                won += 1
            tot_turns += turns
            tot_backups += backups
        if not episodes % STEP:
            mean_duration = (time.time() - time0) * float(1000) / STEP
            if args.validation == 0:
                stats_step = STEP
            else:
                stats_step = args.validation
                # run some validation episodes
                won = tot_turns = tot_backups = 0
                # disable training
                algo.set_params(0)
                algo_play = AlgoPlay()
                for _ in range(stats_step):
                    state = State.create(args.game, random.choice([True, False]))
                    state,turns,backups = Episode(algo_play, PolicyExploit(q)).run(state)
                    if state.player_wins():
                        won += 1
                    tot_turns += turns
                    tot_backups += backups
                # restore training settings
                algo.set_params(alpha)
            # report stats
            rate = 100 * float(won)/stats_step
            mean_td_error  = algo.get_stats()
            log.info('games: %d / won: %.1f%% of %d / avg turns: %.1f / avg backups: %.1f\n'
                     'time: %.2fms/episode / mean td error: %.3f',
                     episodes, rate, stats_step,
                     float(tot_turns)/stats_step,  float(tot_backups)/stats_step,
                     mean_duration, mean_td_error
            )
            won = tot_turns = tot_backups = 0
            algo.reset_stats()
            policy.reset_stats()            
            q.save(epoch=(episodes+args.offset))
            if args.decay:
                # adjust learning rate with decay
                alpha = args.alpha * args.decay / (args.decay+episodes+args.offset)
                log.info('learning rate: %.3f', alpha)
            if args.sarsa > 0:
                # sarsa: adjust exploration rate
                epsilon = args.epsilon * args.sarsa / (args.sarsa+episodes+args.offset)
                log.info('exploration rate: %.3f', epsilon)
            policy.set_params(epsilon, args.softmax)
            algo.set_params(alpha)
            time0 = time.time()
        if episodes == EPISODES:
            break    
    q.save()

    
if __name__ == "__main__":
    train(argparse.ArgumentParser(description='Train the strategy.'))
