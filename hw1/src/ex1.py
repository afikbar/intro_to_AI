import search
import random
import math
from utils import hashabledict, vector_add
from copy import deepcopy

ids = ["111111111", "111111111"]


class State(object):
    wall, pacman, cell = 99, 66, 10
    pills, poison = [11, 21, 31, 41, 51, 71], [71, 77]
    bGhost, yGhost, gGhost, rGhost = [20, 21], [30, 31], [40, 41], [50, 51]

    def __init__(self, grid):
        self.gridDict = {(x, y): ele for x, row in enumerate(grid) for y, ele in enumerate(row)}
        # lookup = {66: 'pacman', 11: 'pills', 21: 'pills', 31: 'pills', 41: 'pills', 51: 'pills', 71: 'pills'}
        # posDtst = {}
        # for key, value in sorted(d.items()):
        #     posDtst.setdefault(value, []).append(key)
        self.pos_dict = {
            'pacman': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele == self.pacman],
            'pills': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele in self.pills],
            'ghosts': {
                'red': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele in self.rGhost],
                'blue': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele in self.bGhost],
                'yellow': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele in self.yGhost],
                'green': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele in self.gGhost]
            },
            'poison': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele in self.poison],
            'walls': [(x, y) for x, row in enumerate(grid) for y, ele in enumerate(row) if ele == self.wall]
        }

        self._pillCnt = len(self.pos_dict['pills'])

    def __eq__(self, other):
        return isinstance(other, State) and self.gridDict == other.gridDict

    def __hash__(self):
        return hash(hashabledict(self.gridDict))  # consider adding hash for ghosts cnt\dist?


class PacmanProblem(search.Problem):
    """This class implements a spaceship problem"""
    directions = {'R': (0, 1), 'D': (1, 0), 'L': (- 1, 0), 'U': (- 1, 0)}  # order matters

    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        # receives the input from main in check.py
        self._size = (len(initial), len(initial[0]))  # size (rows,cols)
        self._firstState = State(initial)
        self.currState = self._firstState
        search.Problem.__init__(self, self._firstState)  # we can change the initial (world as we see it)

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        # define how we do expand in search algo (up,down,left,rigt), for pacman only
        posDict = state.pos_dict
        pRow, pCol = posDict['pacman'][0]  # returns a list.. (for coherentic method)
        moves = {'U': (pRow - 1, pCol), 'R': (pRow, pCol + 1), 'D': (pRow + 1, pCol), 'L': (pRow - 1, pCol)}
        for action, cord in moves:
            if (cord not in posDict['walls']) and (cord not in list(posDict['ghosts'].values())) and (
                    cord not in posDict['poison']):
                yield action

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # ghosts moves here, as "result" from pacman action (moves towards pacman's new pos)
        # min(man_dist to pacman from one of the available slots)
        pacmanX, pacmanY = state.pos_dict['pacman'][0]
        for ghost, cord in state.pos_dict['ghosts'].items():
            pRow, pCol = cord[0]
            moves = {'U': (pRow - 1, pCol), 'R': (pRow, pCol + 1), 'D': (pRow + 1, pCol), 'L': (pRow - 1, pCol)}
            shortest = min(moves, key=lambda k: abs(moves[k][0] - pacmanX) + abs(moves[k][1] - pacmanY)) #what happens if same?

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

    """Feel free to add your own functions"""


def create_pacman_problem(game):
    return PacmanProblem(game)
