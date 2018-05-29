import search
import sys, collections
from utils import hashabledict, vector_add
from copy import deepcopy

ids = ["111111111", "111111111"]

WALL, PACMAN, CELL = 99, 66, 10
PILLS, POISON = [11, 21, 31, 41, 51, 71], [71, 77]
B_GHOST, Y_GHOST, G_GHOST, R_GHOST = [20, 21], [30, 31], [40, 41], [50, 51]
EATEN_BY = 88

DIRECTIONS = {'R': (0, 1), 'D': (1, 0), 'L': (0, -1), 'U': (- 1, 0)}  # order matters


def man_dist(start: tuple, end: tuple) -> int:
    return abs(start[0] - end[0]) + abs(start[1] - end[1])


class State(object):

    def __init__(self, grid):

        self._gridDict = {(x, y): ele for x, row in enumerate(grid) for y, ele in enumerate(row)}
        self.cell_cnt = {cord: 0 for cord in self._gridDict}
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
        return isinstance(other, State) and (self._pill_count.__lt__(other.pill_count))

    def __hash__(self):
        return hash(hashabledict(self._gridDict))  # consider adding hash for ghosts cnt\dist?

    def print(self, depth=0):
        temp = sys.stdout
        sys.stdout = open("temp.txt", 'a')
        print(" State {}:\n".format(depth))
        row = 0
        for cord, ele in self._gridDict.items():
            if row != cord[0]:
                print("\n")
                row = row + 1
            print(ele, ", ", end='')
        print("\n")
        sys.stdout.close()
        sys.stdout = temp

    def closest_pill(self):
        curr = self._pacman
        pills = deepcopy(self._pills)
        # man_dist = lambda cord: abs(cord[0] - curr[0]) + abs(cord[1] - curr[1])
        while pills:
            closest_pill = min(pills, key=lambda pill: man_dist(curr, pill))
            if self.grid[closest_pill] not in POISON:
                yield man_dist(closest_pill, curr)
            pills.remove(closest_pill)
            curr = closest_pill
        return

    def maze_dist(self, start, end):
        visited, queue = set(), collections.deque([start])
        grid = self.grid
        d = 0
        while queue:
            u = queue.popleft()  # front element
            visited.add(u)
            u_adj = [vector_add(u, step) for step in DIRECTIONS.values() if
                     grid[vector_add(u, step)] not in [WALL] + POISON + R_GHOST + B_GHOST + Y_GHOST + G_GHOST]
            for v in u_adj:
                if v not in visited:
                    if v == end:
                        return d + 1
                    visited.add(v)
                    queue.append(v)
            d += 1
        return sys.maxsize


class PacmanProblem(search.Problem):
    """This class implements a spaceship problem"""

    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        # receives the input from main in check.py
        self._size = (len(initial), len(initial[0]))  # size (rows,cols)
        self._first_state = State(initial)
        self._crnt_state = self._first_state
        self._tree = self.build_shortest()
        search.Problem.__init__(self, self._first_state)  # we can change the initial (world as we see it)

    def build_shortest(self):
        return {pill: self.bfs(pill) for pill in self._first_state.pills}

    def bfs(self, start_pos):
        grid = self._first_state.grid
        tree = {cord: sys.maxsize for cord in grid.keys() if cord not in self._first_state.walls}
        visited, queue = set(), collections.deque([start_pos])
        tree[start_pos] = 0
        while queue:
            u = queue.popleft()  # front element
            visited.add(u)
            u_adj = [vector_add(u, step) for step in DIRECTIONS.values() if grid[vector_add(u, step)] != WALL]
            for v in u_adj:
                if v not in visited:
                    visited.add(v)
                    tree[v] = tree[u] + 1
                    queue.append(v)
        return tree

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        # define how we do expand in search algo (up,down,left,rigt), for pacman only
        p_cords = state.pacman
        if p_cords is None or state.grid[p_cords] == EATEN_BY:
            # raise StopIteration # weird error with this
            return
        for action, step in reversed(list(DIRECTIONS.items())):
            cord = vector_add(p_cords, step)  # adds tuples element-wise
            t_cord = p_cords if state.grid[cord] == WALL else cord  # checks if WALL
            ghosts_md = [man_dist(t_cord, g_cord) for g_cord in state.ghosts.values()]
            # keeping 2 steps away from ghost at all time (ghost plays after pacman)
            if all(dist >= 2 for dist in ghosts_md) and (
                    state.grid[cord] not in [WALL] + POISON):  # and state.cell_cnt[cord] < 2:
                yield action

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # ghosts moves here, as "result" from pacman action (moves towards pacman's new pos)
        self._crnt_state = state  # debugging
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
        rslt.cell_cnt[rslt_p_cords] += 1

        # move ghosts:
        for ghost, g_cords in state.ghosts.items():  # order by ghost order (3.6+ dict keeps init order)
            # checks if ghost empty
            moves = {key: vector_add(g_cords, val) for key, val in DIRECTIONS.items() if
                     rslt.grid[vector_add(g_cords, val)] not in [WALL] + B_GHOST + Y_GHOST + G_GHOST + R_GHOST}
            # filters movement to walls.
            # get "shortest" move:
            try:
                shortest = min(list(moves.values()), key=lambda v: man_dist(rslt.pacman, v))
                # what happens if same minimum? gets first min, since order is by DIRECTIONS(3.6+ dict keeps init order)
            except ValueError:
                continue
            # if shortest is null means ghost stuck (thus do nothing)

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

            else:  # empty cell maybe with pill
                rslt.grid[shortest] = (rslt.grid[shortest] % 10) + ghost  # ghost is x0 ghost id
                # changes destination cell to be with ghost (with or without pill)
                rslt.ghosts[ghost] = shortest  # updates new pos

            rslt.grid[g_cords] = rslt.grid[g_cords] - ghost + 10
            # old cords gets update
            # old = pill\empty, new = ghost
        # rslt.print()
        return rslt

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""
        return state.pill_count == 0

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        state = node.state
        if state.pacman is None or state.grid[state.pacman] == EATEN_BY:
            return sys.maxsize

        g_md_poison = 0
        min_ghost_md_poison = sys.maxsize if len(state.ghosts) > 0 else 0  # if there are ghosts init to inf.
        for ghost in state.ghosts.values():  # manhattan distance from ghost to poison+pill
            ghost_pois_md = [man_dist(ghost, poison) for poison in state.poison if state.grid[poison] == POISON[0]]
            g_md_poison += sum(ghost_pois_md)
            min_ghost_md_poison = min(ghost_pois_md + [min_ghost_md_poison])
        poison_pill_cnt = len([x for x in state.poison if x == POISON[0]])  # count pills with poison

        # closest ghost to pacman (L1)
        min_ghst_md_pacman = min([man_dist(state.pacman, ghost) for ghost in state.ghosts.values()], default=0)
        if (len(state.ghosts) == 1 and min_ghst_md_pacman == 1 and poison_pill_cnt) or (
                len(state.ghosts) == 0 and poison_pill_cnt):  # unsolvable
            return sys.maxsize

        ghost_md_max = 0
        for ghost1 in state.ghosts.values():  # manhattan distance from ghost to ghosts (clustered)
            ghost_md = [man_dist(ghost1, ghost2) for ghost2 in state.ghosts.values()]
            ghost_md_max = max(ghost_md + [ghost_md_max])

        # find pills real distance path sum:
        pills = deepcopy(state.pills)
        pills_real_dist_sum = 0
        curr = state.pacman
        if pills:  # skips first pill if poison+pill
            closest = min(pills, key=lambda pill: self._tree[pill][curr])
            if state.grid[closest] != POISON[0] or len(pills) == 1:
                pills_real_dist_sum = state.maze_dist(curr, closest)
                curr = closest
            pills.remove(closest)

        elif len(pills) == 0:
            return 0  # no pills left - we won

        while pills:
            closest = min(pills, key=lambda pill: self._tree[pill][curr])
            pills_real_dist_sum += self._tree[closest][curr]
            curr = closest
            pills.remove(closest)

        # if min_ghst_md_pacman > pills_real_dist_sum:
        #     min_ghst_md_pacman = 0
        """  minimum steps + min ghost dist(L1) to poison + max dist(L1) between ghosts - ghost dist(L1) from pacman """
        return pills_real_dist_sum + min_ghost_md_poison + ghost_md_max - min_ghst_md_pacman * poison_pill_cnt / (node.depth+1)
        # return pills_real_dist_sum + g_md_poison + ghost_md_max - ghost_md_pacman

    """Feel free to add your own functions"""


def create_pacman_problem(game):
    return PacmanProblem(game)
