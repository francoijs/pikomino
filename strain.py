#!/usr/bin/python

import time, sys, signal, argparse
from strategy import episode, s_setparams


DBNAME = 'strategy'
DEFAULT_EPISODES = 100000
DEFAULT_STEP     = 1000
DEFAULT_ALPHA    = .3
DEFAULT_EPSILON  = .1
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
        q = StrategyNetworkQ(DBNAME)
    # counters
    won = all = rate = gain = mark = tot_mark = null = 0
    time0 = time.time()
    while running:
        reward,score = episode(q)
        if reward>0:
            won += 1
            gain += score
        all += 1
        tot_mark += mark
        if score==0:
            null += 1
        if not all % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            null_rate = 100 * float(null)/STEP
            avg_mark = 100 * tot_mark/STEP
            print 'games: %d / won: %.1f%% of last %d / null: %.1f%% / avg score: %.1f / avg mark: %.1f%% / time: %.3fms/game' % (
                all, rate, STEP, null_rate, float(gain)/won if won else 0, avg_mark, perf)
            won = gain = tot_mark = null = 0
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
