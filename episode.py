import copy, random, bisect, logging, math
import numpy as np
from state import State
from algo import algo_qlearning


log = logging.getLogger('episode')
tot_rounds = tot_turns = tot_mark = tot_score = tot_null = won = episodes = 0


class EpisodePiko():

    dbname = 'piko'

    @staticmethod
    def reset_stats():
        global tot_rounds, tot_turns, tot_mark, tot_score, tot_null, won, episodes
        tot_rounds = tot_turns = tot_mark = tot_score = tot_null = won = episodes = 0

    @staticmethod
    def print_stats():
        global tot_rounds, tot_turns, tot_mark, tot_score, tot_null, won, episodes
        if won:
            avg_score = float(tot_score)/won
        else:
            avg_score = 0
        return 'null: %.1f%% / avg score: %.1f / avg mark: %.2f%%' % (
            100 * float(tot_null)/episodes,
            avg_score,
            float(tot_mark)/episodes
        )

    @staticmethod
    def episode(pol_player, pol_opponent=None, algo=algo_qlearning):
        """ Run an episode and return final state. """
        # policy of opponent
        if not pol_opponent:
            pol_opponent = pol_player
        # initial state & action
        state = State()
        action = -1
        my_turn = True
        # number of steal
        turns = rounds = steal = opp_top_tile = 0
        while True:
            if my_turn:
                policy = pol_player
            else:
                policy = pol_opponent
            state,action = algo(policy, state, action)
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
        # stats
        global tot_rounds, tot_turns, tot_mark, tot_score, tot_null, won, episodes
        episodes += 1
        if not my_turn:
            state = state.change_turn()
        if state.player_wins():
            won += 1
            tot_score += state.player_score()
        if state.player_score() == 0:
            tot_null += 1
        tot_mark += steal
        tot_turns += turns
        tot_rounds += rounds
        return state, turns, rounds
