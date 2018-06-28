from copy import deepcopy
import random
import ex3
import math
import time

RESET_CONSTANT = -5
END_OF_LEVEL_CONSTANT = 20
BLOCKING_CODES = (20, 21, 22, 23, 30, 31, 32, 33, 40, 41, 42, 43, 50, 51, 52, 53, 99)
LOSS_INDEXES = (20, 21, 22, 23, 30, 31, 32, 33, 40, 41, 42, 43, 50, 51, 52, 53, 71, 72, 73, 77)
COLOR_CODES = {"red": 50, "green": 40, "blue": 20, "yellow": 30}
WALKABLE_TILES = (10, 11, 12, 13)

# def signal_handler(signum, frame):
#     f.write('Simulation time-out')
#     print('simulation time out')
#     raise Exception("Timed out!")


def create_uniform_probability(a, b):
    def sample_probability():
        return random.uniform(a, b)
    return sample_probability


def create_exponential_probability(mean):
    def sample_probability():
        return random.expovariate(mean)
    return sample_probability


def create_normal_probability(mean, sigma):
    def sample_probability():
        return random.gauss(mean, sigma)
    return sample_probability


def create_lognormal_distribution(mu, alpha):
    def sample_probability():
        return random.lognormvariate(mu, alpha)
    return sample_probability


"""
We can add additional densities! Don't assume we'll use only those four!
"""


def problem_to_state(problem):
    """

    Args:
        problem: pacman problem as tuple of tuples, as described in PDF

    Returns: internal state representation, as dictionary of {coordinate: code} and
    dictionary of objects of special interest (pacman, ghosts, poison) as {name: coordinate}

    """
    state_to_return = {}
    special_things = {"poison": []}

    for number_of_row, row in enumerate(problem):
        for number_of_column, cell in enumerate(row):
            state_to_return[(number_of_row, number_of_column)] = cell
            if cell == 66:
                special_things["pacman"] = (number_of_row, number_of_column)
            elif 50 <= cell <= 53:
                special_things["red"] = (number_of_row, number_of_column)
            elif 40 <= cell <= 43:
                special_things["green"] = (number_of_row, number_of_column)
            elif 30 <= cell <= 33:
                special_things["yellow"] = (number_of_row, number_of_column)
            elif 20 <= cell <= 23:
                special_things["blue"] = (number_of_row, number_of_column)
            elif cell == 77 or cell == 71 or cell == 72 or cell == 73:
                special_things["poison"].append((number_of_row, number_of_column))
    return state_to_return, special_things


def is_action_legal(action):
    if action == "U" or action == "L" or action == "D" or action == "R" or action == "reset":
        return True
    return False


class Evaluator:

    def __init__(self, agent, original_problem, steps, pill_rewards, ghost_probabilities, diagonal_moving_ghosts):
        self.agent = agent
        self.original_problem = deepcopy(original_problem)
        self.state, self.special_things = problem_to_state(original_problem)
        self.accumulated_reward = 0
        self.steps = steps
        self.pill_rewards = pill_rewards
        self.ghost_probabilities = ghost_probabilities
        self.diagonal_moving_ghosts = diagonal_moving_ghosts

    def change_state_after_action(self, action):
        if action == "reset":
            self.reset_field()
            return True
        if self.special_things["pacman"] == "dead":
            raise Exception("Trying to move a dead pacman!")
        self.move_pacman(action)
        order = ["red", "blue", "yellow", "green"]
        random.shuffle(order)
        for color in order:
            if color in self.special_things.keys():
                self.move_ghost(color)
        if self.finished_the_game():
            self.accumulated_reward += END_OF_LEVEL_CONSTANT
            self.reset_field()

    def finished_the_game(self):
        finished = True
        breaking_flag = False
        for i in range(len(self.original_problem)):
            for j in range(len(self.original_problem[0])):
                if 1 <= self.state[(i, j)] % 10 <= 3:
                    finished = False
                    breaking_flag = True
                    break
            if breaking_flag:
                break
        return finished

    def reset_field(self):
        self.state, self.special_things = problem_to_state(self.original_problem)
        self.accumulated_reward += RESET_CONSTANT
        return

    def move_pacman(self, action):
        next_tile = None
        current_tile_x, current_tile_y = self.special_things["pacman"]
        if action == "U":
            next_tile = (current_tile_x - 1, current_tile_y)
        if action == "R":
            next_tile = (current_tile_x, current_tile_y + 1)
        if action == "D":
            next_tile = (current_tile_x + 1, current_tile_y)
        if action == "L":
            next_tile = (current_tile_x, current_tile_y - 1)

        assert next_tile is not None

        # wall
        if self.state[next_tile] == 99:
            return

        # walkable tile
        if self.state[next_tile] in WALKABLE_TILES:
            self.move_pacman_to_walkable_tile((current_tile_x, current_tile_y), next_tile)
            return

        # ghosts and poison
        if self.state[next_tile] in LOSS_INDEXES:
            self.state[next_tile] = 88
            self.state[(current_tile_x, current_tile_y)] = 10
            self.special_things["pacman"] = "dead"

    def move_ghost(self, color):
        ghost_place_x, ghost_place_y = self.special_things[color]
        current_tile = self.special_things[color]
        previous_tile_pill_number = self.state[current_tile] % 10
        previous_tile_contained_pill = 1 <= previous_tile_pill_number <= 3
        ghost_code = COLOR_CODES[color]

        if color in self.diagonal_moving_ghosts:
            adjacent_tiles = [(ghost_place_x - 1, ghost_place_y),
                              (ghost_place_x, ghost_place_y + 1),
                              (ghost_place_x + 1, ghost_place_y),
                              (ghost_place_x, ghost_place_y - 1)]

        else:
            adjacent_tiles = [(ghost_place_x - 1, ghost_place_y),
                              (ghost_place_x, ghost_place_y + 1),
                              (ghost_place_x + 1, ghost_place_y),
                              (ghost_place_x, ghost_place_y - 1),
                              (ghost_place_x - 1, ghost_place_y - 1),
                              (ghost_place_x - 1, ghost_place_y + 1),
                              (ghost_place_x + 1, ghost_place_y + 1),
                              (ghost_place_x + 1, ghost_place_y - 1)
                              ]
        assert adjacent_tiles is not None
        eligible_tiles = [x for x in adjacent_tiles if self.state[x] not in BLOCKING_CODES]
        if len(eligible_tiles) == 0:
            return

        if random.random() <= self.ghost_probabilities[color]:
            # manhattan
            random.shuffle(eligible_tiles)
            next_tile = min(eligible_tiles, key=self.manhattan_distance)
        else:
            # random
            next_tile = random.choice(eligible_tiles)

        # movement result
        # next tile is a regular tile (with or without a pill)
        if 10 <= self.state[next_tile] <= 13:
            self.state[next_tile] = ghost_code + (self.state[next_tile] % 10)
            self.special_things[color] = next_tile

        # poison
        elif self.state[next_tile] == 77 or 70 <= self.state[next_tile] <= 73:
            if self.state[next_tile] == 77:
                self.state[next_tile] = 10
            else:
                self.state[next_tile] = 10 + previous_tile_pill_number
            del self.special_things[color]

        # ghost got the pacman
        elif self.state[next_tile] == 66 or self.state[next_tile] == 88:
            self.special_things["pacman"] = "dead"
            self.state[next_tile] = 88

        if current_tile != next_tile:
            if previous_tile_contained_pill:
                self.state[current_tile] = 10 + previous_tile_pill_number
            else:
                self.state[current_tile] = 10

    def manhattan_distance(self, place_1):
        place_2 = self.special_things["pacman"]
        if place_2 == "dead":
            return 0
        return abs(place_1[0] - place_2[0]) + abs(place_1[1] - place_2[1])

    def state_to_agent(self):
        state_to_return = []
        for row_number in range(len(self.original_problem)):
            current_row = []
            for cell_number in range(len(self.original_problem[row_number])):
                current_row.append(self.state[(row_number, cell_number)])
            state_to_return.append(tuple(current_row))
        return tuple(state_to_return), self.accumulated_reward

    def evaluate_agent(self):
        for step in range(self.steps):
            action = self.agent.choose_next_action(self.state_to_agent()[0], self.state_to_agent()[1])
            if not is_action_legal(action):
                raise Exception("illegal action!", action, "happened at step number:", step)
            self.change_state_after_action(action)
        return self.accumulated_reward

    def move_pacman_to_walkable_tile(self, current_tile, next_tile):
        if self.state[next_tile] == 11:
            self.accumulated_reward += self.pill_rewards["11"]()
        if self.state[next_tile] == 12:
            self.accumulated_reward += self.pill_rewards["12"]()
        if self.state[next_tile] == 13:
            self.accumulated_reward += self.pill_rewards["13"]()
        self.state[next_tile] = 66
        self.state[current_tile] = 10
        self.special_things["pacman"] = next_tile


if __name__ == '__main__':
    problems = (

        ((
             (99, 99, 99, 99, 99, 99, 99),
             (99, 13, 12, 66, 12, 13, 99),
             (99, 11, 11, 11, 11, 11, 99),
             (99, 12, 12, 11, 13, 13, 99),
             (99, 12, 12, 11, 13, 13, 99),
             (99, 12, 12, 11, 13, 13, 99),
             (99, 99, 99, 99, 99, 99, 99),
         ),
         70,
         {"11": create_uniform_probability(0.5, 2), "12": create_exponential_probability(1.5),
          "13": create_exponential_probability(1.7)},
         {"red": 0.9, "green": 0.7, "blue": 0.4, "yellow": 0.4},
         ()),

        ((
         (99, 99, 99, 99, 99, 99, 99),
         (99, 11, 11, 66, 11, 11, 99),
         (99, 11, 11, 11, 11, 11, 99),
         (99, 12, 12, 73, 13, 53, 99),
         (99, 12, 12, 13, 13, 13, 99),
         (99, 12, 12, 13, 13, 13, 99),
         (99, 99, 99, 99, 99, 99, 99),
         ),
         30,
         {"11": create_uniform_probability(0.5, 2), "12": create_exponential_probability(1.5),
          "13": create_exponential_probability(1.7)},
         {"red": 0.9, "green": 0.7, "blue": 0.4, "yellow": 0.4},
         ()),


        ((
             (99, 99, 99, 99, 99, 99, 99),
             (99, 11, 11, 66, 11, 11, 99),
             (99, 11, 11, 11, 11, 11, 99),
             (99, 12, 12, 73, 13, 13, 99),
             (99, 12, 12, 13, 13, 13, 99),
             (99, 12, 12, 53, 13, 13, 99),
             (99, 99, 99, 99, 99, 99, 99),
         ),
         30,
         {"11": create_uniform_probability(0.1, 0.5), "12": create_normal_probability(-1, 0.2),
          "13": create_exponential_probability(0.7)},
         {"red": 0.5, "green": 0.1, "blue": 0.1, "yellow": 0.1},
         ("red",)),
    )

    results = []

    for problem, num_of_steps, pill_rewards_dict, ghost_movement_probabilities, diagonal_moving in problems:
        my_eval = Evaluator(ex3.PacmanController(problem, num_of_steps), problem, num_of_steps,
                            pill_rewards_dict, ghost_movement_probabilities, diagonal_moving)
        results.append(my_eval.evaluate_agent())

    for number, result in enumerate(results):
        print("the result for input", number + 1, "is", result)

