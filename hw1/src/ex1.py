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
    eatenBy = 88

    def __init__(self, grid=None, state=None):
        if state:
            self.gridDict = deepcopy(state.gridDict)
            self.pos_dict = deepcopy(state.pos_dict)
            self._pillCnt = deepcopy(state._pillCnt)
        elif grid:
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

    def __iter__(self):
        return iter(self.gridDict)


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
        pCords = pRow, pCol = posDict['pacman'][0]  # returns a list.. (for coherentic method)
        # moves = {'U': (pRow - 1, pCol), 'R': (pRow, pCol + 1), 'D': (pRow + 1, pCol), 'L': (pRow - 1, pCol)}
        # moves = {key:vector_add(pCords,val) for key,val in self.directions.items()}
        for action, dir in self.directions.items():
            cord = vector_add(pCords, dir)
            if (cord not in list(posDict['ghosts'].values())) and (cord not in posDict['poison']):
                yield action

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # ghosts moves here, as "result" from pacman action (moves towards pacman's new pos)
        # min(man_dist to pacman from one of the available slots)
        rslt = State(None, state)
        posDict = rslt.pos_dict
        pCords = posDict['pacman'][0]
        rslt_pCords = vector_add(pCords, self.directions[action])
        rslt_pCords = pacmanX, pacmanY = pCords if rslt.gridDict[rslt_pCords] == State.wall else rslt_pCords
        # move pacman
        if rslt.gridDict[rslt_pCords] == State.pills[0]:
            rslt._pillCnt = rslt._pillCnt - 1
            rslt.pos_dict['pills'].remove(rslt_pCords)
        rslt.gridDict[pCords], rslt.gridDict[rslt_pCords] = State.cell, State.pacman  # old = cell, new = pacman
        posDict['pacman'][0] = rslt_pCords  # updates posDict

        for ghost, cord in {k: v for k, v in posDict['ghosts'].items() if v}.items():  # order by ghost order
            # checks if cord empty
            gCords = pRow, pCol = cord[0]
            # moves = {'U': (pRow - 1, pCol), 'R': (pRow, pCol + 1), 'D': (pRow + 1, pCol), 'L': (pRow - 1, pCol)}
            moves = {key: vector_add(gCords, val) for key, val in self.directions.items() if
                     rslt.gridDict[vector_add(gCords, val)] not in [State.wall] + list(posDict['ghosts'].values())}
            # filters movement to walls.
            # shortestKey = min(moves, key=lambda k: abs(moves[k][0] - pacmanX) + abs(moves[k][1] - pacmanY))
            shortest = min(list(moves.values()), key=lambda v: abs(v[0] - pacmanX) + abs(v[1] - pacmanY))
            # what happens if same minimum? gets first min, since order is by directions, shoud be ok
            # if shortest is null means ghost stuck
            if (rslt.gridDict[shortest] == State.poison[0]):  # with pill
                rslt.gridDict[shortest] = State.pills[0]
                del posDict['ghosts'][ghost]
                rslt.pos_dict['poison'].remove(shortest)
                # delete ghost and keep pill

            elif rslt.gridDict[shortest] == State.poison[1]:  # no pill
                rslt.gridDict[shortest] = State.cell
                del posDict['ghosts'][ghost]
                rslt.pos_dict['poison'].remove(shortest)

            elif rslt.gridDict[shortest] == State.pacman:  # eats pacman
                rslt.gridDict[shortest] = State.eatenBy
                # TODO:what else??
            else:  # empty cell maybe with pill
                rslt.gridDict[shortest] = (rslt.gridDict[shortest] % 10) + (
                        rslt.gridDict[gCords] - rslt.gridDict[gCords] % 10)  # changes empty cell to ghost with no pill
                posDict['ghosts'][ghost][0] = shortest  # updates posDict

            rslt.gridDict[gCords] = rslt.gridDict[gCords] - (rslt.gridDict[gCords] // 10) * 10 + 10
            # old cords gets update
            # old = pill\empty, new = ghost

            return rslt

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""
        return state._pillCnt == 0

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return node.state._pillCnt


    """Feel free to add your own functions"""


def create_pacman_problem(game):
    return PacmanProblem(game)
