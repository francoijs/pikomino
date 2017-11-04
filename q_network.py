import numpy as np
import os
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam


# 2 sets: dices kept + dices rolled
# per set: 6 sides * (0-8) count of dices per side
# (21-36): value of the smallest available tile
INPUTS = 2*6*9+16
# 12 possibles actions: keep 1 of 6 sides and reroll or stop
OUTPUTS = 12

LEARNING_RATE = 0.001


class NetworkQ:
    def __init__(self, fname):
        self.fname = fname + '.h5'
        if not os.path.isfile(self.fname):
            self.model = self._new_model()
        else:
            self.model = self._load_model(self.fname)

    def _load_model(self, fname):
        #Load
        print 'loading from', self.fname, '...'
        return load_model(fname)
    
    def save(self):
        self.model.save(self.fname)
        print 'saved to', self.fname

    def _new_model(self):
        # Keras/TF
        print 'creating new model %s' % (self.fname)
        model = Sequential()
        model.add(Dense(INPUTS, input_dim=INPUTS, activation='relu'))
        model.add(Dense(INPUTS, activation='relu'))
        model.add(Dense(INPUTS, activation='relu'))
        model.add(Dense(INPUTS, activation='relu'))
        model.add(Dense(OUTPUTS, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=LEARNING_RATE))
        return model

    @staticmethod
    def _inputs(state):
        res = np.zeros((1,INPUTS))
        for s in range(6):
            res[0,s*9+state[0][s]] = 1
            res[0,6*9+s*9+state[1][s]] = 1
        res[0,12*9+state[2]-21] = 1
        return res
#        return np.asmatrix(state[0] + state[1] + [state[2]])
    def get(self, state, action):
        allQ = self.model.predict( self._inputs(state) )
        return allQ[0,action]
    def set(self, state, action, val):
        oldQ = self.model.predict( self._inputs(state) )
        oldQ[0,action] = val
        self.model.fit(self._inputs(state), oldQ, epochs=1, verbose=0)


        
        
        
        
