#!/usr/bin/python

import time, sys, argparse
from piko import episode, roll, setparams
from q_hash import HashQ


def main(argv=sys.argv):
    # parse args
    parser = argparse.ArgumentParser(description='Roll the dices (min score=21).')
    parser.add_argument('target', metavar='T', type=int, default=0, nargs='?',
                        help='target tile: 0,21-36 (default=0: as big as possible)')
    parser.add_argument('--hash', action='store_true',
                        help='use hash table instead of NN')
    args = parser.parse_args()
    print str(args)
    # target param
    target = args.target
    DBNAME = 'q%02d' % (target)
    # playing mode
    setparams(0, 0, log=True, target=target)
    if args.hash:
        from q_hash import HashQ
        q = HashQ(DBNAME)
    else:
        from q_network import NetworkQ
        q = NetworkQ(DBNAME)
    state,reward = episode(([0,0,0,0,0,0], roll(8), 21), q)
    print 'end:',state,reward


if __name__ == "__main__":
    main()
