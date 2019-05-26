# fixes import troubles
import sys, os
sys.path.append('./picomino_play')

import logging
from picomino_play import PicominoNNet, PicominoState, PicominoActions, Replay
from policy import Policy

log = logging.getLogger('policy_jy')


class PolicyJY(Policy):

    def __init__(self):
        self.nnet = PicominoNNet()
        self.nnet.load_checkpoint('picomino_play/temp','best.pth.')

    @property
    def q(self):
        import collections
        q = collections.namedtuple('Q', 'fname')
        q.fname = 'picomino_play/temp/best.pth.'
        return q
        
    def play(self, state):
        # State -> PicominoState
        ps = PicominoState()
        ps.remaining_pico = state.stash
        ps.player1_pico_stack = state.player
        ps.player2_pico_stack = state.opponent
        ps.active_player = 1
        ps.remaining_dices = sum(state.roll)
        ps.rolled_dices = state.roll[1:] + [state.roll[0]]
        ps.kept_dices   = [1 if n else 0 for n in (state.dices[1:] + [state.dices[0]])]
        ps.current_score = state.total()
        ps.nb_turns = 1
        ps.player1_nb_lost_picos = 0
        ps.player2_nb_lost_picos = 0
        # choose action
#        ps.display()
        possible_action_ids = ps.getValidActions()
        log.debug('possible_action_ids: %s', possible_action_ids)
        if not possible_action_ids:
            return -1, [], []
        best_action_id = self.nnet.predict_best_action_id(ps, possible_action_ids)
        action = PicominoActions.action_indexes[best_action_id]
#        print(action.display())
        # convert action
        dice = action.dice_type + 1
        # take dice and reroll
        act = dice if dice<6 else 0
        if not isinstance(action, Replay):
            # take or steal tile
            act = act + 6
        return act, [], []
