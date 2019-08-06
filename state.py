class State:

    @staticmethod
    def create(name, player_starts=True):
        """ Return an instance of initial state for game 'name'. """
        if name == 'piko':
            from state_piko import State
        elif name == 'ttt':
            from state_ttt import State
        elif name == 'test':
            from state_test import StateTest as State
        else:
            raise Exception('unknown game "%s"' % (name,))
        return State(player_starts)

    def report(self, name, prev_state):
        print('<missing report>')

    def end_of_turn(self):
        return True

    def change_turn(self):
        return self

    def find_candidates(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()

    def player_wins(self):
        raise NotImplementedError()

    def opponent_wins(self):
        raise NotImplementedError()
