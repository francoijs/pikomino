#!/usr/bin/python

import time, sys, signal
import piko
from strategy import episode, setparams

DBNAME = 'strategy.db'
EPISODES = 100000
STEP = 1000
running = True

def main():
    # learning mode
    setparams(0.3, 0.1)
    q = piko.loadq(DBNAME)
    # counters
    won = all = rate = gain = mark = tot_mark = 0
    time0 = time.time()
    while running:
        state,reward,score,mark = episode(q)
        if reward>0:
            won += 1
            gain += score
        all += 1
        tot_mark += mark
        if not all % STEP:
            perf = (time.time() - time0) * float(1000) / STEP
            rate = 100 * float(won)/STEP
            avg_mark = 100 * tot_mark/STEP
            print 'games: %d / won: %.1f%% of last %d / avg score: %.1f / avg mark: %.1f%% / time: %.3fms/game' % (
                all, rate, STEP, float(gain)/won if won else 0, avg_mark, perf)
            won = 0
            gain = 0
            tot_mark = 0
            time0 = time.time()
        if all == EPISODES:
            break    
    piko.saveq(DBNAME, q)

def stop(signum, frame):
    print 'stopping...'
    global running
    running = False
    
if __name__ == "__main__":
    # sigterm
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    main()
