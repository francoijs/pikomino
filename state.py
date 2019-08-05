class State:

    @staticmethod
    def create(name):
        """ Return an instance of initial state for game 'name'. """
        if name == 'piko':
            from state_piko import State
        elif name == 'ttt':
            from state_ttt import State
        else:
            raise Exception('unknown game "%s"' % (name,))
        return State()

    def report(self, name, prev_state):
        print('<missing report>')

    def candidates(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()
    def player_wins(self):
        raise NotImplementedError()
    def opponent_wins(self):
        raise NotImplementedError()
