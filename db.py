#!/usr/bin/python

import random, sys
import piko
from q_hash import *


def main(argv=sys.argv):
    # target param
    if len(argv) < 2:
        DBNAME = 'strategy'
        q = StrategyHashQ(DBNAME)
    else:
        DBNAME = 'q%02d' % (int(argv[1]))
        q = HashQ(DBNAME)
    print '%s: %d items' % (DBNAME, len(q))
    print 'min: %.02f / max: %.02f / avg: %.02f / zeros: %.1f%%' % (
        min(q.values()), max(q.values()), sum(q.values())/len(q),
        100*len([p for p in q.values() if p==0])/len(q)
    )
    for idx in range(10):
        print '%s -> %.02f' % (q.keys()[idx], q.values()[idx])

if __name__ == "__main__":
    main()
