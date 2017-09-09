#!/usr/bin/python

import time, sys, signal, random
from piko import episode, roll, setparams
from q_hash import HashQ


DBNAME = 'q.db'
EPISODES = 1000000
STEP = 10000
running = True

def main(argv=sys.argv):
    # target param
    if len(argv) < 2:
        target = 0
    else:
        target = int(argv[1])
    DBNAME = 'q%02d.db' % (target)
    # learning mode
    setparams(0.8, 0.1, target=target)
    q = HashQ(DBNAME)
    # counters
    won = all = rate = gain = 0
    time0 = time.time()
    while running:
        if target == 0:
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
            print 'games: %d / won: %.1f%% of last %d / avg gain: %.1f / time: %.3fms/game' % (all, rate, STEP, float(gain)/won if won else 0, perf)
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
