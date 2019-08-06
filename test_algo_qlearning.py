import random
import logging
from unittest import TestCase
from algo import AlgoQLearning
from policy import PolicyRandom, PolicyExploit
from q_hash import MemoryOnlyHashQ
from episode import Episode
from state_test import StateTest

    
class TestAlgoQLearning(TestCase):

    def setUp(self):        
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s %(name)s: %(message)s"
        )

    def test_update(self):
        q = MemoryOnlyHashQ('test', 3)
        algo = AlgoQLearning(q)
        state0 = StateTest()                # (0,0,0)
        state  = state0.transition(0)       # (1,0,0)
        algo.update(state0, state, 0, 1)    # (0,0,0) -0-> (1,0,0), rwd=1
        # state0 was updated in q
        self.assertListEqual([algo.ALPHA,0,0], q.get_all(state0.inputs())[0].tolist())
        # state is untouched
        self.assertListEqual([0,0,0], q.get_all(state.inputs())[0].tolist())

    def test_train(self):
        q = MemoryOnlyHashQ('test', 3)
        algo = AlgoQLearning(q)
        # train on 10 games
        for _ in range(100):
            ep = Episode(algo, PolicyRandom())
            ep.run(StateTest(random.choice([True, False])))
        # check if policy is optimal
        policy = PolicyExploit(q)
 #       print(q.get_all(StateTest().inputs()))
        for cells, optimal_action in [
                ([0,0,0] , 1),
                ([2,0,0] , 1),
                ([0,0,2] , 1),
        ]:
            state = StateTest()
            state.cells = cells
            self.assertEqual(policy.play(state)[0], optimal_action, state)
