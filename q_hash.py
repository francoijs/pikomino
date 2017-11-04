import os
import cPickle as pickle


class HashQ:
    def __init__(self, fname):
        self.fname = fname = fname + '.db'
        if not os.path.isfile(fname):
            print 'creating empty %s' % (fname)
            self.q = {}
        else:
            with open(fname, 'rb') as file:
                self.q = pickle.load(file)
            print 'loaded %d q-values from' % (len(self.q)), fname
    def __len__(self):
        return len(self.q)
    def keys(self):
        return self.q.keys()
    def values(self):
        return self.q.values()

    @staticmethod
    def _hash(state, action):
        return hash( (tuple(state[0]), tuple(state[1]), state[2], action) )
    def get(self, state, action):
        return self.q.get(self._hash(state,action), 0)
    def set(self, state, action, val):
        self.q[self._hash(state,action)] = val

    def save(self):
        with open(self.fname, 'wb') as file:
            pickle.dump(self.q, file, pickle.HIGHEST_PROTOCOL)
        print '%d q-values saved to' % (len(self.q)), self.fname


class StrategyHashQ(HashQ):
    @staticmethod
    def _hash(state, action):
        return hash(( 0 if not state[0] else min(state[0]),  # smallest available tile
                      0 if not state[1] else state[1][-1],   # opponent top tile
                      state[4] - state[2],                   # score delta
                      action ))                              # action
