#!/usr/bin/python

import time, sys
from piko import episode, roll, loadq, saveq, setparams

DBNAME = 'q.db'
EPISODES = 500000
STEP = 10000

def main(argv=sys.argv):
    # target param
    if len(argv) < 2:
        target = 0
    else:
        target = int(argv[1])
    DBNAME = 'q%02d.db' % (target)
    # learning mode
    setparams(0.3, 0.1, target=target)
    q = loadq(DBNAME)
    # counters
    won = all = rate = gain = 0
    time0 = time.time()
    while True:
        state,reward = episode(([0,0,0,0,0,0], roll(8)), q)
        if (target==0 and reward>0) or (reward==target):
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
    saveq(DBNAME, q)


if __name__ == "__main__":
    main()
