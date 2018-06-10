import random


class Player(object):
    
    def __init__(self, q, EPSILON=0, ALPHA=0):
        self.dqn = q
        self.EPSILON = EPSILON
        self.ALPHA = ALPHA
    
    def policy(self, state):
        """
        Return preferred action for the given state:
        - a in [0-5] : keep dice value a and reroll
        - a in [6-11]: keep dice value a-6 and stop
        - a = -1: no possible action
        """
        candidates = state.find_candidates()
        if len(candidates) == 0:
            # no dice available -> this roll is lost
            return -1, [], [[]]
        allQ = self.dqn.get_all(state.inputs())
        if random.random() < self.EPSILON:
            # exploration
            action = random.choice(candidates)
        else:
            # return best action
            action = candidates[ max(range(len(candidates)), key=lambda i: allQ[0,candidates[i]]) ]
        return action, candidates, allQ

    def update(self, state, action, reward, max_q, oldQ=None):
        if action == -1:
            return
        # update q(state,action)
        if oldQ is None:            
            oldQ = self.dqn.get_all(state.inputs(), action)
        new = oldQ[0,action] + self.ALPHA * ( reward + max_q - oldQ[0,action] )
        self.dqn.set(state.inputs(), action, new, oldQ)
