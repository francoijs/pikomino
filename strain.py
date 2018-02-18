#!/usr/bin/python

import time, sys, signal, argparse
from strategy import episode, s_setparams


DBNAME = 'strategy'
DEFAULT_EPISODES = 100000
DEFAULT_STEP     = 1000
DEFAULT_ALPHA    = .3
DEFAULT_EPSILON  = .1
DEFAULT_LAYERS   = 3
running = True

def main():
    # parse args
    parser = argparse.ArgumentParser(description='Train the strategy.')
    parser.add_argument('--episodes', '-e', metavar='N', type=int, default=DEFAULT_EPISODES,
                        help='total number of episodes (default=%d)'%(DEFAULT_EPISODES))
    parser.add_argument('--step', '-s', metavar='S', type=int, default=DEFAULT_STEP,
                        help='number of episodes per step (default=%d)'%(DEFAULT_STEP))
    parser.add_argument('--hash', action='store_true',
                        help='use hash table instead of NN')
    parser.add_argument('--alpha', metavar='ALPHA', type=float, default=DEFAULT_ALPHA,
                        help='learning rate (default=%.3f)'%(DEFAULT_ALPHA))
    parser.add_argument('--epsilon', metavar='EPSILON', type=float, default=DEFAULT_EPSILON,
                        help='exploration ratio (default=%.3f)'%(DEFAULT_EPSILON))
    parser.add_argument('--layers', '-l', metavar='L', type=int, default=DEFAULT_LAYERS,
                        help='number of hidden layers (default=%d)'%(DEFAULT_LAYERS))
    parser.add_argument('--debug', '-d', action='store_true', default=False, 
                        help='display debug log')
    args = parser.parse_args()
    print str(args)
    # params of training
    EPISODES = args.episodes
    STEP     = args.step
    # learning mode
    s_setparams(args.alpha, args.epsilon, log=args.debug)
    if args.hash:
        from q_hash import StrategyHashQ
        q = StrategyHashQ(DBNAME)
    else:
        from q_network import StrategyNetworkQ
        q = StrategyNetworkQ(DBNAME, layers=args.layers)
    # counters
    won = all = rate = tot_score = mark = tot_mark = tot_null = tot_rounds = 0
    time0 = time.time()
    while running:
        reward,score,mark,rounds = episode(q)
        if reward>0:
            won += 1
            tot_score += score
        all += 1
        tot_mark += mark
        tot_rounds += rounds
        if score==0:
            tot_null += 1
        mark = score = 0
        if not all % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            null_rate = 100 * float(tot_null)/STEP
            avg_mark = float(tot_mark)/STEP
            if won:
                avg_score = float(tot_score)/won
            else:
                avg_score = 0
            print 'games: %d / won: %.1f%% of last %d / rounds: %.1f/game / null: %.1f%% / avg score: %.1f / avg mark: %.1f%% / time: %.3fms/game' % (
                all, rate, STEP, float(tot_rounds)/STEP, null_rate, avg_score, avg_mark, perf)
            won = tot_null = tot_score = tot_mark = tot_rounds = 0
            q.save(epoch=all)
            time0 = time.time()
        if all == EPISODES:
            break    
    q.save()

def stop(signum, frame):
    print 'stopping...'
    global running
    running = False
    
if __name__ == "__main__":
    # sigterm
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    main()
