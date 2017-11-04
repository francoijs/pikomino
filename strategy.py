import piko, copy, random, bisect
from q_hash import HashQ
from q_network import NetworkQ


S_LOG = False
S_ALPHA = 0.3    # learning rate
S_EPSILON = 0.1

class sortedlist(list):
    '''just a list but with an insort (insert into sorted position)'''
    def insort(self, x):
        bisect.insort(self, x)

def s_setparams(alpha, epsilon, log=False):
    global S_ALPHA, S_EPSILON, S_LOG
    S_ALPHA = alpha
    S_EPSILON = epsilon
    print 'strategy: alpha=%.1f / epsilon=%.1f' % (S_ALPHA, S_EPSILON)
    # deactivate learning when rolling dices
    piko.setparams(0,0)
    S_LOG = log

def episode(q):
    """ Run an episode and return final state, reward, my score """
    mine = []
    opponent = []
    tiles = sortedlist(range(21,37))
    state = (tiles, opponent, 0, mine, 0)
    mark = all_mark = 0
    my_turn = True
    # eligibility traces for this episode (no decay)
    traces = []
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
                target_q = loadq(0)   # regular roll
                smallest = tiles[0]
#                smallest = min([tiles[0]] + [opp[-1] for opp in [state[1]] if opp])
            else:
                target_q = loadq(state[1][-1])   # aim at opponent tile
                smallest = 21
            # roll
            roll_state,roll_reward = piko.episode(([0,0,0,0,0,0], piko.roll(8), smallest), target_q)
            score = piko.score(roll_state)
            if action > 0:
                all_mark += 1
                if roll_reward > 0:
                    mark += 1   # sniping succeeded
            if S_LOG:
                print 'my roll:' if my_turn else 'opponent roll:', score
            state = transition(state, score)
            reward = 0
            qsa = max([q.get(state,a) for a in range(2)])
        # record trace
        # FIXME: disabled, no apparent effect on perfs
        traces.append( (state0, action, reward+qsa) )
        # update q(state0,action)
        old = q.get(state0, action)
        new = old + S_ALPHA * ( reward + qsa - old )
        q.set(state0, action, new)
        if S_LOG:
            print state0, '--|%d|->' % (action), state
        if reward != 0:
            break
        my_turn = not my_turn
    mark_rate = 0 if all_mark==0 else float(mark)/all_mark
    # update back traces
    while traces:
        trace = traces.pop()
        old = q.get(trace[0], trace[1])
        new = old + S_ALPHA * ( trace[2] - old )
        q.set(trace[0], trace[1], new)        
    return state, reward, state[4], mark_rate

def transition(state, roll):
    if state[1] and roll==state[1][-1]:
        # take tile of opponent
        state[3].append(state[1].pop())
    else:
        tiles,tile = _take(state[0], roll)
        if not tile:
            # no tile available with this roll -> give back 1 tile
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
    if random.random() < S_EPSILON:
        # exploration
        return random.choice(candidates)
    # return best action
    return candidates[ max(range(len(candidates)), key=lambda i: q.get(state,candidates[i])) ]

# tables of Q-values
allq = {
    # use a network for target=0
    0: NetworkQ('q00')
}
def loadq(action):
    if action not in allq:
        # use hash tables for all other targets
        allq[action] = HashQ('q%02d' % (action))
    return allq[action]
