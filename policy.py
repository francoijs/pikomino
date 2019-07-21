import logging, random
import numpy as np

log = logging.getLogger('policy')


class Policy(object):

    @staticmethod
    def create(typ, q=None):
        if typ is 'softmax':
            return PolicySoftmax(q)
        elif typ is 'egreedy':
            return PolicyEGreedy(q)
        elif typ is 'exploit':
            return PolicyExploit(q)
        elif typ is 'random':
            return PolicyRandom()
        else:
            raise 'unknown policy type <%d>' % (typ,)

    def __init__(self, q):
        self.q = q
    
    @property
    def name(self):
        return self.q.fname

    def set_params(self, epsilon, temperature):
        self.EPSILON = epsilon
        self.TEMPERATURE = temperature
        log.debug('policy: epsilon=%.2f / temperature=%.2f',
                  self.EPSILON, self.TEMPERATURE)    


class PolicySoftmax(Policy):

    def __init__(self, q, temperature=0):
        Policy.__init__(self, q)
        self.TEMPERATURE = temperature      # softmax temperature
        self.sum_max_softmax = 0
        self.count_softmax = 0

    def reset_stats(self):
        self.sum_max_softmax = self.count_softmax = 0

    def get_stats(self):
        if self.count_softmax == 0:
            return 0
        return float(self.sum_max_softmax) / self.count_softmax
    
    def softmax(self, q_vector):
        """
        Return a softmax distribution of the values in q_vector.
        """
        q_vector = np.exp(q_vector / self.TEMPERATURE)
        q_vector /= np.sum(q_vector)
        # fix normalization
        q_vector[np.argmax(q_vector)] += 1-np.sum(q_vector)
        self.sum_max_softmax += max(q_vector)
        self.count_softmax += 1
        return q_vector

    def play(self, state):
        """
        Return preferred action for the given state:
        - a in [0-5] : keep dice value a and reroll
        - a in [6-11]: keep dice value a-6 and stop
        - a = -1: no possible action
        """
        candidates = state.find_candidates()
        log.debug('candidates for %s: %s', state, candidates)    
        if len(candidates) == 0:
            # no dice available -> this roll is lost
            return -1, [], np.empty((0,0))
        allQ = self.q.get_all(state.inputs())
        # softmax distribution
        ps = np.zeros(len(candidates))
        idx = 0
        for c in candidates:
            ps[idx] = allQ[0,c]
            idx += 1
        action = np.random.choice(candidates, p=self.softmax(ps))
        return action, candidates, allQ


class PolicyEGreedy(Policy):

    def __init__(self, q, epsilon=0.1):
        Policy.__init__(self, q)
        self.EPSILON     = epsilon    # exploration ratio

    def reset_stats(self):
        pass

    def get_stats(self):
        return 0
    
    def play(self, state):
        """
        Return preferred action for the given state:
        - a in [0-5] : keep dice value a and reroll
        - a in [6-11]: keep dice value a-6 and stop
        - a = -1: no possible action
        """
        candidates = state.find_candidates()
        log.debug('candidates for %s: %s', state, candidates)    
        if len(candidates) == 0:
            # no dice available -> this roll is lost
            return -1, [], np.empty((0,0))
        allQ = self.q.get_all(state.inputs())
        if random.random() < self.EPSILON:
            # e-greedy exploration
            action = random.choice(candidates)
        else:
            # exploitation: return best action
            action = candidates[ max(list(range(len(candidates))), key=lambda i: allQ[0,candidates[i]]) ]
        return action, candidates, allQ


class PolicyExploit(PolicyEGreedy):
    def __init__(self, q):
        PolicyEGreedy.__init__(self, q, 0)
    

class PolicyRandom(Policy):
    def __init__(self):
        Policy.__init__(self, None)
    
    @property
    def name(self):
        return 'random policy'
    
    def play(self, state):
        candidates = state.find_candidates()
        log.debug('candidates for %s: %s', state, candidates)    
        if len(candidates) == 0:
            # no dice available -> this roll is lost
            return -1, [], np.empty((0,0))
        action = random.choice(candidates)
        return action, candidates, np.empty((0,0))
