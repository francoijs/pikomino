import piko, copy, random, bisect

LOG = False
ALPHA = 0.3    # learning rate
EPSILON = 0.1

class sortedlist(list):
    '''just a list but with an insort (insert into sorted position)'''
    def insort(self, x):
        bisect.insort(self, x)

def setparams(alpha, epsilon, log=False):
    global ALPHA, EPSILON, LOG
    ALPHA = alpha
    EPSILON = epsilon
    LOG = log

def episode(q):
    """ Run an episode and return final state, reward, my score """
    mine = []
    opponent = []
    tiles = sortedlist(range(21,37))
    state = (tiles, opponent, 0, mine, 0)
    my_turn = True
    while True:
        if my_turn:
            state = (tiles, opponent, state[4], mine, state[2])
        else:
            state = (tiles, mine, state[4], opponent, state[2])
        state0 = copy.deepcopy(state)
        action = policy(state, q)
        if action == -1:
            # game is over
            if state[2] < state[4]:
                qsa = reward = 1    # win
            else:
                qsa = reward = -1   # loss or draw
        else:
            if action==0 or len(state[1])==0:
                target_q = loadq(0)   # aim at biggest possible tile
            else:
                target_q = loadq(state[1][-1])   # aim at opponent tile
            # roll
            _, score = piko.episode(([0,0,0,0,0,0], piko.roll(8)), target_q)
            if LOG:
                print 'my roll:' if my_turn else 'opponent roll:', score
            state = transition(state, score)
            reward = 0
            qsa = max([getq(q,state,a) for a in range(37)])
        # update q(state0,action)
        old = getq(q, state0, action)
        new = old + ALPHA * ( reward + qsa - old )
        setq(q, state0, action, new)
        if LOG:
            print state0, '--|%d|->' % (action), state
        if reward != 0:
            break
        my_turn = not my_turn
    return state,reward,state[4]

def transition(state,action):
    if state[1] and action==state[1][-1]:
        # take tile of opponent
        state[3].append(state[1].pop())
    else:
        tiles,tile = _take(state[0], action)
        if not tile:
            # no tile available with this action -> give back 1 tile
            if state[3]:
                tiles = _give(tiles, state[3].pop())
            if tiles:
                tiles.pop()
        else:
            # new tile on top of mine
            state[3].append(tile)
    return (state[0],
            state[1], score(state[1]),
            state[3], score(state[3])
    )

def score(tiles):
    """ Return score yielded by a set of tiles """
    score = 0
    for t in tiles:
        if   t<25: score += 1
        elif t<29: score += 2
        elif t<33: score += 3
        else:      score += 4
    return score

def _take(tiles,tile):
    while tile > 20:
        if tile in tiles:
            tiles.remove(tile)
            return tiles,tile
        tile -= 1
    return tiles,None
def _give(tiles,tile):
    tiles.insort(tile)
    return tiles

def policy(state, q):
    """
    Return preferred action for the given state:
    - 0: make biggest possible score
    - 1: aim for tile of opponent
    """
    candidates = []
    # remaining tiles?
    if not state[0]:
        return -1
    # available tiles
    candidates += [0]
    # tile of opponent
    if state[1]:
        candidates = candidates + [1]
    if random.random() < EPSILON:
        # exploration
        return random.choice(candidates)
    # return best action
    return candidates[ max(range(len(candidates)), key=lambda i: getq(q,state,candidates[i])) ]

def _hash(state, action):
    return hash(( tuple(state[0]),                                 # sorted available tiles
                  0 if not state[1] else state[1][-1], state[2],   # opponent top tile and score
                  0 if not state[3] else state[3][-1], state[4] )) # my top tile and score
def getq(q, state, action):
    return q.get(_hash(state,action), 0)
def setq(q, state, action, val):
    q[_hash(state,action)] = val

allq = {}
def loadq(action):
    if action not in allq:
        allq[action] = piko.loadq('q%02d.db' % (action))
    return allq[action]
