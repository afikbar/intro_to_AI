import search
import random
import math

ids = ["111111111", "111111111"]


class State(object):
    def __init__(self, grid):
        self.pos_dict = {
            'pacman': [(ix, iy) for ix, row in enumerate(grid) for iy, i in enumerate(row) if i == 66],
            'pills': [(ix, iy) for ix, row in enumerate(grid) for iy, i in enumerate(row) if
                      i in [11, 21, 31, 41, 51, 71]],
            'ghosts': {
                'blue': [(ix, iy) for ix, row in enumerate(grid) for iy, i in enumerate(row) if i in [20, 21]],
                'yellow': [(ix, iy) for ix, row in enumerate(grid) for iy, i in enumerate(row) if i in [30, 31]],
                'green': [(ix, iy) for ix, row in enumerate(grid) for iy, i in enumerate(row) if i in [40, 41]],
                'red': [(ix, iy) for ix, row in enumerate(grid) for iy, i in enumerate(row) if i in [50, 51]],
            },
            'poison': [(ix, iy) for ix, row in enumerate(grid) for iy, i in enumerate(row) if i in [71, 77]],
        }

        self._pillCnt = len(self.pos_dict['pills'])

    def __eq__(self, other):
        return isinstance(other, State) and self._pillCnt == other._pillCnt

    def __hash__(self):
        return hash(self._pillCnt)  # consider adding hash for ghosts cnt\dist?


class PacmanProblem(search.Problem):
    """This class implements a spaceship problem"""

    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        # receives the input from main in check.py
        self._size = (len(initial), len(initial[0]))  # size (rows,cols)

        search.Problem.__init__(self, initial)  # we can change the initial (world as we see it)

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        # define how we do expand in search algo (up,down,left,rigt), for pacman only

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # ghosts moves here, as "result" from pacman action (moves towards pacman's new pos)
        # min(man_dist to pacman from one of the available slots)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

    """Feel free to add your own functions"""


def create_pacman_problem(game):
    return PacmanProblem(game)
