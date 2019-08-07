# pylint: disable=multiple-imports,import-error

import os, logging
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np


LEARNING_RATE = 0.001
log = logging.getLogger('network_q')


class NetworkQ():

    def __init__(self, fname, inputs=0, outputs=0, layers=3, width=0):
        if fname.find('.h5') == -1:
            if width == 0:
                width = inputs
            fname = '%s-inputs%d-hidden%d-width%d.h5' % (fname, inputs, layers, width)
        self.fname = fname
        if not os.path.isfile(self.fname):
            self.model = self._new_model(inputs, outputs, layers, width)
        else:
            self.model = self._load_model(self.fname)
        for layer in self.model.layers:
            log.info('layer %s: %d / %s', layer.name, layer.units, layer.activation.__name__)
        # cache
        self._cache_state = None
        self._cache_q = None

    def _new_model(self, inputs, outputs, layers, width):
        # Keras/TF
        log.info('creating new model %s', self.fname)
        model = Sequential()
        model.add(Dense(inputs, input_dim=inputs, activation='relu'))
        while layers>0:
            model.add(Dense(width, activation='relu'))
            layers -= 1
        model.add(Dense(outputs, activation='linear'))
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
        if not np.array_equal(self._cache_state, state):
            self._cache_state = state
            self._cache_q = self.model.predict(state)
        return self._cache_q
    
    def get(self, state, action):
        return self.get_all(state)[0,action]
    def set(self, state, action, val, oldQ=None):
        if oldQ is None:
            oldQ = self.model.predict(state)
        oldQ[0,action] = val
        self.model.fit(state, oldQ, epochs=1, verbose=0)
