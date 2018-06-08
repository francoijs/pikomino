#!/usr/bin/python

import logging
from strategy import episode, s_setparams


DBNAME = 'strategy'

logging.basicConfig(level=logging.INFO)


def main():
    # playing mode
    s_setparams(0, 0, debug=True)
    from q_network import StrategyNetworkQ
    q = StrategyNetworkQ(DBNAME)
    reward,score,_,_ = episode(q)
    print 'end:',reward,score


if __name__ == "__main__":
    main()
