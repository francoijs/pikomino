#!/usr/bin/python

import time
from piko import episode, roll, loadq

DBNAME = 'q.db'

def main():
    q = loadq(DBNAME)
    state,reward = episode(([0,0,0,0,0,0], roll(8)), q)
    print 'end:',state,reward


if __name__ == "__main__":
    main()
