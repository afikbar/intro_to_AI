import time
import random

import sys, collections
from utils import hashabledict, vector_add
from copy import deepcopy

ids = ["311121289", "961152147"]

WALL, PACMAN, CELL = 99, 66, 10
PILLS, POISON = [11,12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43, 51, 52, 53,  71, 72, 73], [71, 72, 73, 77]
B_GHOST, Y_GHOST, G_GHOST, R_GHOST = [20, 21, 22, 23], [30, 31, 32 ,33], [40, 41, 42 ,43], [50, 51, 52 ,53]
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
        self.pills_init_weight()

    def pills_init_weight(self):
        self.pills_weight = {}
        for num in PILLS:
            self.pills_weight[num] = 1

    def get_pill_weight(self, p_coord):
        num = self._gridDict[p_coord[0], p_coord[1]]
        return self.pills_weight[num]

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

    def choose_next_action(self, state, accumulated_reward):
        """Choose next action for pacman controller given the current state.
        Action should be returned in the format described previous parts of the project.
        This method MUST terminate within the specified timeout."""
        # print('COMPLETE choose_next_action')
        curr_state = State(state)
        p_cords = curr_state.pacman
        if p_cords is None:
            return "reset"

        poison_pill_cnt = len([x for x in curr_state.poison if x == POISON[0]])  # count pills with poison
        if poison_pill_cnt == 1 and curr_state.pill_count == 1:
            moves = {key: vector_add(p_cords, val) for key, val in DIRECTIONS.items() if
                     curr_state.grid[vector_add(p_cords, val)] not in [WALL, POISON[
                         1]] + B_GHOST + Y_GHOST + G_GHOST + R_GHOST}
        else:
            moves = {key: vector_add(p_cords, val) for key, val in DIRECTIONS.items() if
                     curr_state.grid[vector_add(p_cords, val)] not in [
                         WALL] + POISON + B_GHOST + Y_GHOST + G_GHOST + R_GHOST}
        if not moves:
            return "reset"
        flee_moves1, flee_moves2 = [], []
        if curr_state.ghosts.values() and curr_state.pill_count > 1:
            try:
                blue_ghst_md = man_dist(curr_state.ghosts[20], p_cords)
            except:
                blue_ghst_md = sys.maxsize
            closest_ghst = min(curr_state.ghosts.values(), key=lambda g_cords: man_dist(p_cords, g_cords))
            min_ghst_md_pacman = man_dist(p_cords, closest_ghst)
            # if len(curr_state.ghosts) == 1 and min_ghst_md_pacman == 1 and poison_pill_cnt:  # unsolvable
            #     return "reset"
            if blue_ghst_md <= 3:
                flee_moves1 = sorted(moves, key=lambda d: man_dist(moves[d], curr_state.ghosts[20]), reverse=True)[:1]
            if min_ghst_md_pacman <= 2:  # flee mode
                flee_moves2 = sorted(moves, key=lambda key: man_dist(moves[key], closest_ghst), reverse=True)[:1]
        if flee_moves1 or flee_moves2:
            moves = {k: moves[k] for k in set(flee_moves1 + flee_moves2)}
        closest_pill = min(curr_state.pills, key=lambda p: self.shortest_trees[p][p_cords]/curr_state.get_pill_weight(p))
        shortest = min(moves, key=lambda key: self.shortest_trees[closest_pill][moves[key]])

        return shortest

    def h(self, state):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
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

        """  minimum steps + min ghost dist(L1) to poison + max dist(L1) between ghosts - ghost dist(L1) from pacman """
        return pills_real_dist_sum + min_ghost_md_poison + ghost_md_max - min_ghst_md_pacman
        # return pills_real_dist_sum + g_md_poison + ghost_md_max - ghost_md_pacman


    """Feel free to add your own functions"""

    def random_walk(self, state, accumulated_reward):
        """Choose next action for pacman controller given the current state.
        Action should be returned in the format described previous parts of the project.
        This method MUST terminate within the specified timeout.
        """

        "random walk agent"
        for row in state:
            print(row)
        print("________")
        alive = False
        for row in state:
            for cell in row:
                if cell == 66:
                    alive = True
                    break
            if alive:
                break
        if not alive:
            return "reset"
        return random.choice(["U", "D", "L", "R"])
        # print('COMPLETE choose_next_action')



def create_pacman_problem(game):
    return PacmanController(game)


