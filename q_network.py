import numpy as np
import os
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam


LEARNING_RATE = 0.001
INPUTS = 16+16+16+81+2*6*9   # 261
# 12 possibles actions: keep 1 of 6 sides and reroll or stop
OUTPUTS = 12

class StrategyNetworkQ():

    def __init__(self, fname, layers=3):
        self.fname = '%s-%dhidden.h5' % (fname, layers)
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

    def get(self, state, action):
        allQ = self.model.predict(state)
        return allQ[0,action]
    def set(self, state, action, val):
        oldQ = self.model.predict(state)
        oldQ[0,action] = val
        self.model.fit(state, oldQ, epochs=1, verbose=0)
