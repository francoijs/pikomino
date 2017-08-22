#!/usr/bin/python

import time
from piko import episode, roll, loadq, saveq, setparams

DBNAME = 'q.db'
EPISODES = 100000
STEP = 10000

def main():
    # learning mode
    setparams(0.3, 0.1)
    q = loadq(DBNAME)
    # counters
    won = all = rate = gain = 0
    time0 = time.time()
    while True:
        state,reward = episode(([0,0,0,0,0,0], roll(8)), q)
        if reward > 0:
            won += 1
            gain += reward
        all += 1
        if not all % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            print 'games: %d / won: %.1f%% of last %d / avg gain: %.1f / time: %.3fms/game' % (all, rate, STEP, float(gain)/won, perf)
            won = 0
            gain = 0
            time0 = time.time()
        if all == EPISODES:
            break    
    saveq(DBNAME, q)


if __name__ == "__main__":
    main()
