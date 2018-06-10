# pylint: disable=multiple-imports,import-error

import os, logging
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam
from state import State


LEARNING_RATE = 0.001
INPUTS = State.INPUTS
# 12 possibles actions: keep 1 of 6 sides and reroll or stop
OUTPUTS = 12
log = logging.getLogger('StrategyNetworkQ')


class StrategyNetworkQ():

    def __init__(self, fname, layers=3):
        if fname.find('.h5') == -1:
            fname = '%s-%dinputs-%dhidden.h5' % (fname, INPUTS, layers)
        self.fname = fname
        if not os.path.isfile(self.fname):
            self.model = self._new_model(layers)
        else:
            self.model = self._load_model(self.fname)

    def _new_model(self, layers):
        # Keras/TF
        log.info('creating new model %s', self.fname)
        model = Sequential()
        model.add(Dense(INPUTS, input_dim=INPUTS, activation='relu'))
        while layers>0:
            model.add(Dense(INPUTS, activation='relu'))
            layers -= 1
        model.add(Dense(OUTPUTS, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=LEARNING_RATE))
        return model

    def _load_model(self, fname):
        #Load
        log.info('loading from %s...', self.fname)
        return load_model(fname)
    
    def save(self, epoch=0):
        if epoch:
            epoch = '-'+str(epoch)
        else:
            epoch = ''
        self.model.save(self.fname+epoch)
        log.info('saved to '+self.fname+epoch)

    def get_all(self, state):
        return self.model.predict(state)
    def get(self, state, action):
        return self.get_all(state)[0,action]
    def set(self, state, action, val, oldQ=None):
        if oldQ is None:
            oldQ = self.model.predict(state)
        oldQ[0,action] = val
        self.model.fit(state, oldQ, epochs=1, verbose=0)
