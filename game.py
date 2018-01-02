#!/usr/bin/python

import time, sys, piko
from strategy import episode, s_setparams
from q_hash import StrategyHashQ


DBNAME = 'strategy'

def main():
    # playing mode
    s_setparams(0, 0, log=True)
    from q_network import StrategyNetworkQ
    q = StrategyNetworkQ(DBNAME)
    reward,score = episode(q)
    print 'end:',reward,score


if __name__ == "__main__":
    main()
