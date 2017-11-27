from unittest import TestCase
from strategy import transition,sortedlist

class TestStrategy(TestCase):
    def test_transition(self):
        data = [
            # from stash
            ( ([21,22,23],[],0,[],0)   , 25, ([21,22],[],0,[23],1) ),
            ( ([21,22,27,28],[],0,[],0), 25, ([21,27,28],[],0,[22],1) ),
            # steal
            ( ([21,22,23],[25],2,[],0) , 25, ([21,22,23],[],0,[25],2) ),
            ( ([31,32,33],[25],2,[],0) , 25, ([31,32,33],[],0,[25],2) ),
            # loss
            ( ([31,32,33],[24],1,[27],2), 25, ([27,31,32],[24],1,[],0) ),
            ( ([31,32,33],[24],1,[34],2), 25, ([31,32,33],[24],1,[],0) ),
            ( ([31,32,33],[24],1,[27],2), 0, ([27,31,32],[24],1,[],0) ),
            ( ([31,32,33],[24],1,[34],2), 0, ([31,32,33],[24],1,[],0) ),
        ]
        for d in data:
            inp = d[0]
            inp = (sortedlist(inp[0]),inp[1],inp[2],inp[3],inp[4])
            roll = d[1]
            out = d[2]
            out = (sortedlist(out[0]),out[1],out[2],out[3],out[4])
            self.assertEqual(transition(inp,roll), out)
