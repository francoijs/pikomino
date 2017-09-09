#!/usr/bin/python

import time, sys, piko
from strategy import episode, setparams
from q_hash import StrategyHashQ


DBNAME = 'strategy.db'

def main():
    # playing mode
    setparams(0, 0, log=True)
    q = StrategyHashQ(DBNAME)
    state,reward,score,mark = episode(q)
    print 'end:',state,reward,score,mark


if __name__ == "__main__":
    main()
