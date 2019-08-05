import logging
import copy
import unittest
import mock
from episode import Episode
from state_test import StateTest
from policy import PolicyRandom
from q_hash import MemoryOnlyHashQ
from algo import AlgoQLearning

class CopyingMock(mock.MagicMock):

    def __call__(self, *args, **kwargs):
        args = copy.deepcopy(args)
        kwargs = copy.deepcopy(kwargs)
        return super(CopyingMock, self).__call__(*args, **kwargs)
    

class TestEpisode(unittest.TestCase):

    def setUp(self):        
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s %(name)s: %(message)s"
        )
        self.policy = PolicyRandom()
        self.policy.play = mock.MagicMock()
        self.algo = AlgoQLearning(MemoryOnlyHashQ('', StateTest.OUTPUTS))
        self.algo.update = CopyingMock()

    def test_player_starts_and_draw(self):
        self.policy.play.side_effect = [(0,0,0), (2,0,0)]
        ep = Episode(self.algo, self.policy)
        self.assertEqual((-.5, 3, 3), ep.run(StateTest()))
        self.assertEqual(2, self.algo.update.call_count)

    def test_player_starts_and_wins(self):
        self.policy.play.side_effect = [(1,0,0), (2,0,0)]
        ep = Episode(self.algo, self.policy)
        self.assertEqual((1, 3, 3), ep.run(StateTest()))
        self.assertEqual(2, self.algo.update.call_count)

    def test_opponent_starts_and_wins(self):
        self.policy.play.side_effect = [(2,0,0)]
        ep = Episode(self.algo, self.policy)
        self.assertEqual((-1, 3, 3), ep.run(StateTest(2)))
        self.assertEqual(1, self.algo.update.call_count)

    def test_opponent_starts_and_draw(self):
        self.policy.play.side_effect = [(1,0,0)]
        ep = Episode(self.algo, self.policy)
        self.assertEqual((-.5, 3, 3), ep.run(StateTest(2)))
        self.assertEqual(1, self.algo.update.call_count)
