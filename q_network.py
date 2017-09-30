import tensorflow as tf
import numpy as np


INPUTS = 12*9+16
OUTPUTS = 12

class NetworkQ:
    def __init__(self, fname):
        print 'creating network'
        self.fname = fname
        # TF
        tf.reset_default_graph()
        #These lines establish the feed-forward part of the network used to choose actions
        self.inputs = tf.placeholder(shape=[1,INPUTS], dtype=tf.float32)
        self.W = tf.Variable(tf.random_uniform([INPUTS,OUTPUTS], 0, 0.01))
        self.Qout = tf.matmul(self.inputs, self.W)
#        self.predict = tf.argmax(Qout,1)
        #Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
        self.nextQ = tf.placeholder(shape=[1,OUTPUTS], dtype=tf.float32)
        loss = tf.reduce_sum(tf.square(self.nextQ - self.Qout))
        trainer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
        self.updateModel = trainer.minimize(loss)
        init = tf.global_variables_initializer()
        session = tf.Session()
        session.run(init)
        return session

    def save(self):
        #Create a saver object which will save all the variables
        saver = tf.train.Saver()
        #Now, save the graph
        saver.save(self.session, self.fname, global_step=0)
        print 'saved to', self.fname

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
        allQ = self.session.run(self.Qout,feed_dict={self.inputs:self._inputs(state)})
        return allQ[0,action]
    def set(self, state, action, val):
        oldQ = self.session.run(self.Qout,feed_dict={self.inputs:self._inputs(state)})
        oldQ[0,action] = val
        #Train our network using target and predicted Q values
        _,W1 = self.session.run([self.updateModel, self.W],
                                feed_dict={self.inputs:self._inputs(state),self.nextQ:oldQ})

        
        
        
        
