import time
import random
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



class PacmanController:
    """This class is a controller for a pacman agent."""

    def __init__(self, state, steps):
        """Initialize controller for given the initial setting.
        This method MUST terminate within the specified timeout."""
        # print('COMPLETE init ')
        self.first_state = State(state)
        self.shortest_trees = self.build_shortest_trees()

    def build_shortest_trees(self):
        return {pill: self.bfs(pill) for pill in self.first_state.pills}

    def bfs(self, start_pos):
        grid = self.first_state.grid
        tree = {cord: sys.maxsize for cord in grid.keys() if cord not in self.first_state.walls}
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

    def choose_next_action(self, state):
        """Choose next action for pacman controller given the current state.
        Action should be returned in the format described previous parts of the project.
        This method MUST terminate within the specified timeout."""
        # print('COMPLETE choose_next_action')
        curr_state = State(state)
        p_cords = curr_state.pacman
        if p_cords is None:
            return "reset"

        moves = {key: vector_add(p_cords, val) for key, val in DIRECTIONS.items() if
                 curr_state.grid[vector_add(p_cords, val)] not in
                 [WALL]}
        if not moves:
            return "reset"

        poison_pill_cnt = len([x for x in curr_state.poison if x == POISON[0]])  # count pills with poison
        if curr_state.ghosts.values():
            try:
                blue_ghst_md = man_dist(curr_state.ghosts[20], p_cords)
            except:
                blue_ghst_md = sys.maxsize
            closest_ghst = min(curr_state.ghosts.values(), key=lambda g_cords: man_dist(p_cords, g_cords))
            min_ghst_md_pacman = man_dist(p_cords, closest_ghst)
            if len(curr_state.ghosts) == 1 and min_ghst_md_pacman == 1 and poison_pill_cnt:  # unsolvable
                return "reset"

            if (min_ghst_md_pacman <= 2) or (blue_ghst_md<=3):  # flee mode
                flee_move = max(moves, key=lambda key: man_dist(moves[key], closest_ghst))
                # flee_move_b =
                return flee_move

        closest_pill = min(curr_state.pills, key=lambda p: self.shortest_trees[p][p_cords])
        # shortest = min(moves, key=lambda key: man_dist(moves[key], closest_pill))
        shortest = min(moves, key=lambda key: self.shortest_trees[closest_pill][moves[key]])

        return shortest