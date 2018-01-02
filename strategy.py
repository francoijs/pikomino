import copy, random, bisect
import numpy as np
from q_hash import HashQ


LOG = False
ALPHA = 0.3    # learning rate
EPSILON = 0.1

class sortedlist(list):
    '''just a list but with an insort (insert into sorted position)'''
    def insort(self, x):
        bisect.insort(self, x)

def s_setparams(alpha, epsilon, log=False):
    global ALPHA, EPSILON, LOG
    ALPHA = alpha
    EPSILON = epsilon
    print 'strategy: alpha=%.1f / epsilon=%.1f' % (ALPHA, EPSILON)
    LOG = log

def episode(q):
    """ Run an episode and return final state, reward, my score """
    mine = []
    opponent = []
    tiles = sortedlist(range(21,37))
    # initial state
    #        stash  his       mine  dices          roll
    state = (tiles, opponent, mine, [0,0,0,0,0,0], roll(8))
    my_turn = True
    while True:
        state0 = copy.deepcopy(state)
        action,candidates = policy(state, q)
        if LOG:
            print 'candidates:', state, ':', candidates
        state = transition(state, action)
        # end of game?
        if not state[0]:
            # no more tiles in stash
            if (my_turn and score(state[1])<score(state[2])) or (not my_turn and score(state[1])>=score(state[2])):
                qsa = reward = 1    # win
            else:
                qsa = reward = -1   # loss or draw
        else:
            # game not over
            reward = 0
            if candidates:
                qsa = max([q.get(_inputs(state),a) for a in candidates])
            else:
                qsa = 0
        # update q(state0,action)
        old = q.get(_inputs(state0), action)
        new = old + ALPHA * ( reward + qsa - old )
        q.set(_inputs(state0), action, new)
        # log transition
        if LOG:
            print 'transition:', state0, '--|%d|->' % (action), state
        if reward != 0:
            # game is over
            break
        # change player?
        if sum(state[3]) == 0:
            if my_turn:
                mine = state[2]
                opponent = state[1]
                state = (state[0], mine, opponent, state[3], state[4])
            else:
                mine = state[1]
                opponent = state[2]
                state = (state[0], opponent, mine, state[3], state[4])
            my_turn = not my_turn
    return reward, score(mine)

def transition(state, action):
    """ Apply action on state and return new state. """
    if action == -1:
        # give back 1 tile
        tiles = sortedlist(state[0])
        if state[2]:
            tiles = _give(tiles, state[2].pop())
        if tiles:
            # remove biggest tile
            tiles.pop()
        return (tiles,
                state[1], state[2],
                [0,0,0,0,0,0], roll(8)
        )
    if action<6:
        # keep some dices then reroll
        state[3][action] += state[4][action]
        reward = 0
        return (state[0],state[1],state[2],state[3],roll(8-sum(state[3])))
    else:
        state = transition(state, action-6)
        if state[1] and total(state)==state[1][-1]:
            # take tile of opponent
            state[2].append(state[1].pop())
        else:
            # take tile from stash?
            tiles,tile = _take(state[0], total(state))
            if not tile:
                # no tile available with this total -> give back 1 tile
                if state[2]:
                    state[0] = _give(tiles, state[2].pop())
                if state[0]:
                    # remove biggest tile
                    state[0].pop()
            else:
                # new tile on top of mine
                state[2].append(tile)
    return (state[0], state[1], state[2],
            [0,0,0,0,0,0], roll(8)
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
    - a in [0-5] : keep dice value a and reroll
    - a in [6-11]: keep dice value a-6 and stop
    - a = -1: no possible action
    """
    candidates = find_candidates(state)
    if len(candidates) == 0:
        # no dice available -> this roll is lost
        action = -1
    elif random.random() < EPSILON:
        # exploration
        action = random.choice(candidates)
    else:
        # return best action
        action = candidates[ max(range(len(candidates)), key=lambda i: q.get(_inputs(state),candidates[i])) ]
    return action, candidates

def find_candidates(state):
    """ Return list of candidates actions """
    assert sum(state[3]) + sum(state[4]) == 8
    # dices that may be kept before rerolling
    candidates = [n for n in range(6) if state[4][n]>0 and state[3][n]==0]
    # dices that may be kept before stopping
    stop = []
    for action in candidates:
        if action==0:
            new_score = total(state) + state[4][0]*5
            if new_score >= state[0][0] or ( state[1] and state[1][-1] == new_score):
                stop.append(6)
        else:
            # cannot stop if score not at least bigger than the smallest available tile
            new_score = total(state) + state[4][action]*action
            if action and not state[3][0]:
                new_score = 0
            if state[0][0] and ( new_score>=state[0][0] or (state[1] and state[1][-1] == new_score) ):
                stop.append(6+action)
    return candidates + stop

def roll(n):
    """ Roll n dices and return 6-array with count for each value """
    roll = [0,0,0,0,0,0]
    draw = [random.randint(0,5) for _ in range(n)]
    for d in draw:
        roll[d] += 1
    return roll

def total(state):
    return 5*state[3][0] + sum([n*state[3][n] for n in range(6)])
    
def _policy(state, q):
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
    return candidates[ max(range(len(candidates)), key=lambda i: q.get(_inputs(state),candidates[i])) ]


# 16 possible tiles in stash
# 16 possible top opponent tiles [21,36]
# 16 possible top mine tiles [21,36]
# 81 possible score deltas [-40,40]
# 2 sets: dices kept + dices rolled
# per set: 6 sides * (0-8) count of dices per side
INPUTS = 16+16+16+81+2*6*9   # 261
# 12 possibles actions: keep 1 of 6 sides and reroll or stop
OUTPUTS = 12

def _inputs(state):
    res = np.zeros((1,INPUTS))
    ptr = 0
    # stash
    for t in state[0]:
        res[0,ptr+t-21] = 1
    ptr += 16
    # opponent top tile
    if state[1]:
        res[0,ptr+state[1][-1]] = 1
    ptr += 16
    # my top tile
    if state[2]:
        res[0,ptr+state[2][-1]] = 1
    ptr += 16
    # score delta
    res[0,ptr+score(state[3])-score(state[2])+40] = 1  # score delta
    ptr += 81
    # dices
    for s in range(6):
        res[0,ptr+s*9+state[3][s]] = 1
    ptr += 6*9
    # roll
    for s in range(6):
        res[0,ptr+s*9+state[4][s]] = 1
    return res
