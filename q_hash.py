import os
#import cPickle as pickle
import pickle
import logging
import numpy as np


log = logging.getLogger('q_hash')

class HashQ:

    def __init__(self, fname, outputs):
        self.outputs = outputs
        self.fname = fname = fname + '.db'
        if not os.path.isfile(fname):
            log.info('creating empty %s', fname)
            self.q = {}
        else:
            with open(fname, 'rb') as fil:
                self.q = pickle.load(fil)
            log.info('loaded %d q-vectors from %s', len(self.q), fname)

    def __len__(self):
        return len(self.q)
    def keys(self):
        return self.q.keys()
    def values(self):
        return self.q.values()

    def get_all(self, state):
        return self.q.get(hash(tuple(state.tolist()[0])), np.zeros((1, self.outputs)))
    def get(self, state, action):
        allQ = self.get_all(state)
        return allQ[action]
    def set(self, state, action, val, oldQ=None):
        if oldQ is None:
            oldQ = self.get_all(state)
        oldQ[0,action] = val
        self.q[hash(tuple(state.tolist()[0]))] = oldQ
        log.debug('%s\t%s', state.tolist()[0], oldQ)

    def save(self, epoch=0):
        if epoch:
            epoch = '-'+str(epoch)
        else:
            epoch = ''
        with open(self.fname+epoch, 'wb') as fil:
            pickle.dump(self.q, fil, pickle.HIGHEST_PROTOCOL)
        log.info('%d q-vectors saved to %s', len(self.q), self.fname+epoch)


class MemoryOnlyHashQ(HashQ):

    def __init__(self, fname, outputs):
        self.outputs = outputs
        self.fname = 'unused'
        self.q = {}
        log.info('create memory-only q-table')

    def save(self, epoch=0):
        pass
