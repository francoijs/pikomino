#!/usr/bin/python

def C(r, n):
    r = min(r, n-r)
    if r == 0: return 1
    res = 1
    for k in range(1,r+1):
        res = res*(n-k+1)/k
    return res

for i in range(9):
    print 'rolls w/ %d dices: '%(i), C(5,i+5)
print 'rolls w/ 0-8 dices: ', sum([ C(5,i+5) for i in range(9) ])

S = sum([ C(5,i+5) * sum([ C(5,k+5) for k in range(9-i) ]) for i in range(9) ])
print 'keeps and rolls w/ 0-8 dices: ', S
print 'smallest tile (21-36) & keeps and rolls w/ 0-8 dices: ', S * 16
print 'all tiles (21-36) & keeps and rolls w/ 0-8 dices: ', S * 2**16
