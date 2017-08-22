#!/usr/bin/python

import time
from piko import episode, roll, loadq, setparams

DBNAME = 'q.db'

def main():
    # playing mode
    setparams(0, 0, log=True)
    q = loadq(DBNAME)
    state,reward = episode(([0,0,0,0,0,0], roll(8)), q)
    print 'end:',state,reward


if __name__ == "__main__":
    main()
