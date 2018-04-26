import search
import random
import math
import sys
from utils import hashabledict, vector_add
from copy import deepcopy

ids = ["111111111", "111111111"]

WALL, PACMAN, CELL = 99, 66, 10
PILLS, POISON = [11, 21, 31, 41, 51, 71], [71, 77]
B_GHOST, Y_GHOST, G_GHOST, R_GHOST = [20, 21], [30, 31], [40, 41], [50, 51]
EATEN_BY = 88

DIRECTIONS = {'R': (0, 1), 'D': (1, 0), 'L': (0, -1), 'U': (- 1, 0)}  # order matters


class State(object):
    # TODO: rethink state object (remove static vars, getters\setters for pos, etc)
    # TODO: design as Predicats? atoms of True.
    last_state = 0  # static

    def __init__(self, grid):
        State.last_state = State.last_state + 1
        self._state_num = State.last_state

        self._gridDict = {(x, y): ele for x, row in enumerate(grid) for y, ele in enumerate(row)}
        self._pacman = next((cord for cord, ele in self._gridDict.items() if ele == PACMAN), None)
        self._pills = [cord for cord, ele in self._gridDict.items() if ele in PILLS]
        self._poison = [cord for cord, ele in self._gridDict.items() if ele in POISON]
        self._walls = [cord for cord, ele in self._gridDict.items() if ele == WALL]
        self._ghosts = {
            R_GHOST[0]: next((cord for cord, ele in self._gridDict.items() if ele in R_GHOST), None),
            B_GHOST[0]: next((cord for cord, ele in self._gridDict.items() if ele in B_GHOST), None),
            Y_GHOST[0]: next((cord for cord, ele in self._gridDict.items() if ele in Y_GHOST), None),
            G_GHOST[0]: next((cord for cord, ele in self._gridDict.items() if ele in G_GHOST), None)
        }
        self._ghosts = {k: v for k, v in self._ghosts.items() if v}  # removes keys with empty values
        self._pill_count = len(self._pills)

    @property
    def grid(self):
        return self._gridDict

    @grid.setter
    def grid(self, dict):
        self._gridDict = dict

    @property
    def pacman(self):
        return self._pacman

    @pacman.setter
    def pacman(self, cord):
        self._pacman = cord

    @property
    def pills(self):
        return self._pills

    @pills.setter
    def pills(self, list):
        self._pills = list

    @property
    def poison(self):
        return self._poison

    @poison.setter
    def poison(self, list):
        self._poison = list

    @property
    def walls(self):
        return self._walls

    @walls.setter
    def walls(self, walls_list):
        self._walls = walls_list

    @property
    def ghosts(self):
        return self._ghosts

    @ghosts.setter
    def ghosts(self, ghosts_dict):
        self._ghosts = ghosts_dict

    @property
    def pill_count(self):
        return self._pill_count

    @pill_count.setter
    def pill_count(self, val):
        self._pill_count = val

    def __eq__(self, other):
        return isinstance(other, State) and self._gridDict.__eq__(other.grid)

    def __lt__(self, other):
        return isinstance(other, State) and self._pill_count.__lt__(other.pill_count)

    def __hash__(self):
        return hash(hashabledict(self._gridDict))  # consider adding hash for ghosts cnt\dist?

    def print(self):
        print(" State {}:\n".format(self._state_num))
        row = 0
        for cord, ele in self._gridDict.items():
            if row != cord[0]:
                print("\n")
                row = row + 1
            print(ele, ", ", end='')
        print("\n")


class PacmanProblem(search.Problem):
    """This class implements a spaceship problem"""

    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        # receives the input from main in check.py
        self._size = (len(initial), len(initial[0]))  # size (rows,cols)
        self._first_state = State(initial)
        self._crnt_state = self._first_state
        search.Problem.__init__(self, self._first_state)  # we can change the initial (world as we see it)

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        # define how we do expand in search algo (up,down,left,rigt), for pacman only
        p_cords = state.pacman
        if state.grid[p_cords] == EATEN_BY:
            return
        for action, step in DIRECTIONS.items():
            cord = vector_add(p_cords, step)  # adds tuples element-wise
            ghosts_md = map(lambda g_cord: abs(g_cord[0] - cord[0]) + abs(g_cord[1] - cord[1]), state.ghosts.values())
            # keeping 2 steps away from ghost at all time (ghost plays after pacman)
            if all(dist >= 2 for dist in ghosts_md) and (cord not in POISON):
                yield action

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # ghosts moves here, as "result" from pacman action (moves towards pacman's new pos)
        # min(man_dist to pacman from one of the available slots)
        rslt = deepcopy(state)
        p_cords = state.pacman
        if rslt.grid[p_cords] == EATEN_BY:  # if pacman was eaten dont play
            return rslt
        rslt_p_cords = vector_add(p_cords, DIRECTIONS[action])  # gets aimed cell
        rslt_p_cords = p_cords if rslt.grid[rslt_p_cords] == WALL else rslt_p_cords  # checks if WALL
        # move pacman:
        if rslt.grid[rslt_p_cords] == PILLS[0]:
            rslt.pill_count -= 1
            rslt.pills.remove(rslt_p_cords)
        rslt.grid[p_cords], rslt.grid[rslt_p_cords] = CELL, PACMAN  # old = cell, new = pacman
        rslt.pacman = rslt_p_cords  # updates position

        # move ghosts:
        for ghost, g_cords in rslt.ghosts.items():  # order by ghost order
            # checks if ghost empty
            moves = {key: vector_add(g_cords, val) for key, val in DIRECTIONS.items() if
                     rslt.grid[vector_add(g_cords, val)] not in [WALL] + list(rslt.ghosts.values())}
            # filters movement to walls.
            # get "shortest" move:
            try:
                shortest = min(list(moves.values()),
                               key=lambda v: abs(v[0] - rslt.pacman[0]) + abs(v[1] - rslt.pacman[1]))
                # what happens if same minimum? gets first min, since order is by DIRECTIONS, shoud be ok
            except ValueError:
                continue
            # if shortest is null means ghost stuck

            if rslt.grid[shortest] == POISON[0]:  # poison + pill
                rslt.grid[shortest] = PILLS[0]
                del rslt.ghosts[ghost]
                rslt.poison.remove(shortest)
                # delete ghost and keep pill

            elif rslt.grid[shortest] == POISON[1]:  # poison only
                rslt.grid[shortest] = CELL
                del rslt.ghosts[ghost]
                rslt.poison.remove(shortest)

            elif rslt.grid[shortest] == PACMAN:  # eats pacman
                rslt.grid[shortest] = EATEN_BY
                rslt.ghosts[ghost] = shortest
                # TODO:what else??

            else:  # empty cell maybe with pill
                rslt.grid[shortest] = (rslt.grid[shortest] % 10) + ghost  # ghost is x0 ghost id
                # changes destination cell to be with ghost (with or without pill)
                rslt.ghosts[ghost] = shortest  # updates new pos

            rslt.grid[g_cords] = rslt.grid[g_cords] - ghost + 10
            # old cords gets update
            # old = pill\empty, new = ghost
            return rslt

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""
        return state.pill_count == 0

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        # TODO: prefer board where ghosts are near poison+pill?
        # TODO: prefer eat pills in direction of ghosts and then runaway?
        # TODO: remove "bad effect" to gain best estimate (i.e. duplicate positions without deleteing)
        if node.state.grid[node.state.pacman] == EATEN_BY:
            return sys.maxsize
        return node.state.pill_count

    """Feel free to add your own functions"""


def create_pacman_problem(game):
    return PacmanProblem(game)
