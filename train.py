#!/usr/bin/python

import time, sys, signal, random, argparse
from piko import episode, roll, setparams


DEFAULT_EPISODES = 15000
DEFAULT_STEP     = 500
DEFAULT_ALPHA    = .8
DEFAULT_EPSILON  = .1
running = True

def main(argv=sys.argv):
    # parse args
    parser = argparse.ArgumentParser(description='Train to roll the dices.')
    parser.add_argument('target', metavar='T', type=int, default=0, nargs='?',
                        help='target tile: 0,21-36 (default=0: as big as possible)')
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
    args = parser.parse_args()
    print str(args)
    # params of training
    EPISODES = args.episodes
    STEP     = args.step
    target   = args.target
    DBNAME = 'q%02d' % (target)
    # learning mode
    setparams(args.alpha, args.epsilon, target=target)
    if args.hash:
        from q_hash import HashQ
        q = HashQ(DBNAME)
    else:
        from q_network import NetworkQ
        q = NetworkQ(DBNAME)
    # counters
    won = all = rate = gain = 0
    time0 = time.time()
    while running:
        if target==0:
            smallest = random.randint(21,36)
        else:
            smallest = 21
        state,reward = episode(([0,0,0,0,0,0], roll(8), smallest), q)
        if (target==0 and reward>0) or (reward==100):
            won += 1
            gain += reward
        all += 1
        if not all % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            print 'episodes: %d / won: %.1f%% of last %d / avg gain: %.1f / time: %.3fms/episode' % (all, rate, STEP, float(gain)/won if won else 0, perf)
            won = 0
            gain = 0
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
