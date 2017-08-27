#!/usr/bin/python

import time, sys, piko
from strategy import episode, loadq, setparams

DBNAME = 'strategy.db'

def main():
    # playing mode
    setparams(0, 0, log=True)
    q = piko.loadq(DBNAME)
    state,reward,score = episode(q)
    print 'end:',state,reward,score


if __name__ == "__main__":
    main()
