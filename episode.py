import copy, random, bisect, logging, math
import numpy as np
from state import State
from algo import algo_qlearning


log = logging.getLogger('episode')

def episode(q_player, q_opponent=None, algo=algo_qlearning):
    """ Run an episode and return final state. """
    # DQN of opponent
    if not q_opponent:
        q_opponent = q_player
    # initial state & action
    state = State()
    action = -1
    my_turn = True
    # number of steal
    turns = rounds = steal = opp_top_tile = 0
    while True:
        if my_turn:
            q = q_player
        else:
            q = q_opponent
        state,action = algo(q, state, action)
        rounds += 1
        if state.end_of_game():
            # game is over
            break
        # change player?
        if state.end_of_turn():
            turns += 1
            if state.player and state.player[-1]==opp_top_tile:
                steal += 1
            if state.player:
                opp_top_tile = state.player[-1]
            else:
                opp_top_tile = 0
            state = state.change_turn()
            action = -1
            my_turn = not my_turn
    return (state if my_turn else state.change_turn()), steal, turns, rounds
