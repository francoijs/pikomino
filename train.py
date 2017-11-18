#!/usr/bin/python

import time, sys, signal, random, argparse
from piko import episode, roll, setparams


DEFAULT_EPISODES = 15000
DEFAULT_STEP     = 500
DEFAULT_ALPHA    = .5
DEFAULT_EPSILON  = .1
VALIDATION_RATIO = .2
DEFAULT_LAYERS   = 3
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
    parser.add_argument('--layers', '-l', metavar='L', type=int, default=DEFAULT_LAYERS,
                        help='number of hidden layers (default=%d)'%(DEFAULT_LAYERS))
    parser.add_argument('--decay', metavar='K', type=int, default=0,
                        help='learning rate decay (default=off)')
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
        q = NetworkQ(DBNAME, args.layers)
    
    # counters
    won = all = rate = gain = 0
    time0 = time.time()
    while running:
        if target==0:
            smallest = 21
        else:
            smallest = 21
        episode(([0,0,0,0,0,0], roll(8), smallest), q)
        all += 1
        if not all % STEP:
            if target==0:
                # validation
                setparams(0, 0, target=target)
                rewards = []
                won = gain = 0
                for _ in range(int(VALIDATION_RATIO*STEP)):
                    _,reward = episode(([0,0,0,0,0,0], roll(8), 21), q)
                    if (target==0 and reward>0) or (reward==100):
                        won += 1
                        gain += reward
                    rewards.append(reward)
                rate = 100 * float(won) / (VALIDATION_RATIO*STEP)
                # continue learning (with decay if required)
                if args.decay:
                    alpha = args.alpha * args.decay / (args.decay+all)
                setparams(alpha, args.epsilon, target=target)
            perf = (time.time() - time0) * float(1000) / STEP
            print 'train: episodes: %d / time: %.3fms/ep | test: won: %.1f%% of %d / avg gain: %.1f' % (all, perf, rate, VALIDATION_RATIO*STEP, float(gain)/won if won else 0)
            time0 = time.time()
        if all == EPISODES:
            break

    # save model before exit
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
