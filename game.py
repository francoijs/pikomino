#!/usr/bin/python

import time, sys, piko
from strategy import episode, loadq, setparams

DBNAME = 'strategy.db'

def main():
    # playing mode
    setparams(0, 0, log=True)
    q = piko.loadq(DBNAME)
    state,reward,score,mark = episode(q)
    print 'end:',state,reward,score,mark


if __name__ == "__main__":
    main()
