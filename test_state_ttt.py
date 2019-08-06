import numpy
from unittest import TestCase
from state_ttt import State


class TestStateTtt(TestCase):
    
    def test_find_candidates(self):
        data = [
            ( ([None] * 9, '0')                                         , [0,1,2,3,4,5,6,7,8] ),
            ( (['0', None, '1', None, '0', None, '1', None, '0'] , '0') , [1,3,5,7] ),
            ( ([None, '1', None, '0', None, '1', None, '0', None], '0') , [0,2,4,6,8] ),
            ( (['0', None, '1', None, '0', None, '1', None, '0'] , '0') , [1,3,5,7] ),
            ( (['0', '1', '0', '0', '1', '0', '1', '1', '0']     , '0') , [] ),
       ]
        for d in data:
            cells  = d[0][0]
            cands = d[1]
            state = State()
            state.cells = cells
            self.assertEqual(state.find_candidates(), cands)

    def test_transition(self):
        data = [
            #  input state                              , action
            #  output state                             , reward
            # choose and change turn
            ( ([None, None, None,
                None, None, None,
                None, None, None], '0')                 , 4 ,
              ([None, None, None,
                None, '0' , None,
                None, None, None], '1')                 , 0 ),
            ( ([None, None, None,
                None, None, None,
                None, None, None], '1')                 , 4 ,
              ([None, None, None,
                None, '1' , None,
                None, None, None], '0')                 , 0 ),
            ( ([None, '0' , None,
                '1' , None, None,
                None, None, '1' ], '0')                 , 4 ,
              ([None, '0' , None,
                '1' , '0' , None,
                None, None, '1' ], '0')                 , 0 ),
            # '0' wins
            ( ([None, '0' , None,
                '1' , '0' , None,
                None, None, '1' ], '0')                 , 7 ,
              ([None, '0' , None,
                '1' , '0' , None,
                None, '0', '1'  ], '1')                 , 1 ),
            # '1' wins
            ( ([None, '0' , None,
                '0' , '1' , None,
                None, None, '1' ], '1')                 , 0 ,
              (['1' , '0' , None,
                '0' , '1' , None,
                None, None, '1' ], '0')                 , 1 ),
            # draw
            ( (['1' , '0' , '0' ,
                '0' , '1' , '1' ,
                None, '0' , '0' ], '1')                 , 6 ,
              (['1' , '0' , '0' ,
                '0' , '1' , '1' ,
                '1' , '0' , '0' ], '0')                 , -1 ),
        ]
        for d in data:
            inp = d[0]
            action = d[1]
            out = d[2]
            state0 = State(inp[1] == '0')
            state0.cells = inp[0]
            state1 = State(out[1] == '0')
            state1.cells = out[0]
            self.assertEqual(state0.transition(action), state1)


    def test_inputs(self):
        data = [
            ( ([None, '0' , None,
                '0' , '1' , None,
                None, None, '1' ] , '0'),
              [1,0,0, 0,1,0, 1,0,0,
               0,1,0, 0,0,1, 1,0,0,
               1,0,0, 1,0,0, 0,0,1
              ] ),
            ( ([None, '0' , None,
                '0' , '1' , None,
                None, None, '1' ] , '1'),
              [1,0,0, 0,0,1, 1,0,0,
               0,0,1, 0,1,0, 1,0,0,
               1,0,0, 1,0,0, 0,1,0
              ] )
        ]
        for d in data:
            inp = d[0]
            out = d[1]
            state = State(inp[1] == '0')
            state.cells = inp[0]
            numpy.testing.assert_array_equal(state.inputs()[0], out)
