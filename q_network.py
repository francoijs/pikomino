import numpy as np
import os
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam
from state import State


LEARNING_RATE = 0.001
INPUTS = State.INPUTS
# 12 possibles actions: keep 1 of 6 sides and reroll or stop
OUTPUTS = 12

class StrategyNetworkQ():

    def __init__(self, fname, layers=3):
        self.fname = '%s-%dinputs-%dhidden.h5' % (fname, INPUTS, layers)
        if not os.path.isfile(self.fname):
            self.model = self._new_model(layers)
        else:
            self.model = self._load_model(self.fname)

    def _new_model(self, layers):
        # Keras/TF
        print 'creating new model %s' % (self.fname)
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
        print 'loading from', self.fname, '...'
        return load_model(fname)
    
    def save(self):
        self.model.save(self.fname)
        print 'saved to', self.fname

    def get_all(self, state):
        return self.model.predict(state)
    def get(self, state, action):
        return self.get_all(state)[0,action]
    def set(self, state, action, val):
        oldQ = self.model.predict(state)
        oldQ[0,action] = val
        self.model.fit(state, oldQ, epochs=1, verbose=0)
