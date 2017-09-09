#!/usr/bin/python

import time, sys
from piko import episode, roll, setparams
from q_hash import HashQ


DBNAME = 'q.db'

def main(argv=sys.argv):
    # target param
    if len(argv) < 2:
        target = 0
    else:
        target = int(argv[1])
    DBNAME = 'q%02d.db' % (target)
    # playing mode
    setparams(0, 0, log=True, target=target)
    q = HashQ(DBNAME)
    state,reward = episode(([0,0,0,0,0,0], roll(8), 21), q)
    print 'end:',state,reward


if __name__ == "__main__":
    main()
