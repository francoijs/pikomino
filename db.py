#!/usr/bin/python

import random, sys
import piko

def main(argv=sys.argv):
    # target param
    if len(argv) < 2:
        DBNAME = 'strategy.db'
    else:
        DBNAME = 'q%02d.db' % (int(argv[1]))
    q = piko.loadq(DBNAME)
    print '%s: %d items' % (DBNAME, len(q))
    for idx in range(10):
        print '%s -> %.02f' % (q.keys()[idx], q.values()[idx])

if __name__ == "__main__":
    main()
