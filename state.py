class State:

    @staticmethod
    def create(name):
        """ Return an instance of initial state for game 'name'. """
        if name == 'piko':
            from state_piko import State
        elif name == 'ttt':
            from state_ttt import State
        else:
            raise 'unknown game "%s"' % (name,)
        return State()

    def report(self, name, prev_state):
        print('<missing report>')
