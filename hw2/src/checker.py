from copy import deepcopy
import random
import ex2
import time

PILL_CONSTANT = 1
RESET_CONSTANT = -20
END_OF_LEVEL_CONSTANT = 50
PROBABILITIES = {"red": 0.9, "green": 0.7, "blue": 0.4, "yellow": 0.4}
BLOCKING_CODES = (20, 21, 30, 31, 40, 41, 50, 51, 99)
LOSS_INDEXES = (20, 21, 30, 31, 40, 41, 50, 51, 71, 77)
COLOR_CODES = {"red": 50, "green": 40, "blue": 20, "yellow": 30}

# def signal_handler(signum, frame):
#     f.write('Simulation time-out')
#     print('simulation time out')
#     raise Exception("Timed out!")


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
                print("Pacman position is:", number_of_row, number_of_column)
            elif cell == 50 or cell == 51:
                special_things["red"] = (number_of_row, number_of_column)
            elif cell == 40 or cell == 41:
                special_things["green"] = (number_of_row, number_of_column)
            elif cell == 30 or cell == 31:
                special_things["yellow"] = (number_of_row, number_of_column)
            elif cell == 20 or cell == 21:
                special_things["blue"] = (number_of_row, number_of_column)
            elif cell == 77 or cell == 71:
                special_things["poison"].append((number_of_row, number_of_column))
    return state_to_return, special_things


def is_action_legal(action):
    if action == "U" or action == "L" or action == "D" or action == "R" or action == "reset":
        return True
    return False


class Evaluator:

    def __init__(self, agent, original_problem, steps):
        self.agent = agent
        self.original_problem = deepcopy(original_problem)
        self.state, self.special_things = problem_to_state(original_problem)
        self.accumulated_reward = 0
        self.steps = steps

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
            self.accumulated_reward += 50
            self.reset_field()

    def finished_the_game(self):
        finished = True
        breaking_flag = False
        for i in range(len(self.original_problem)):
            for j in range(len(self.original_problem[0])):
                if self.state[(i, j)] % 10 == 1:
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
        if self.state[next_tile] == 10 or self.state[next_tile] == 11:
            if self.state[next_tile] == 11:
                self.accumulated_reward += PILL_CONSTANT
            self.state[next_tile] = 66
            self.state[(current_tile_x, current_tile_y)] = 10
            self.special_things["pacman"] = next_tile
            return

        # ghosts and poison
        if self.state[next_tile] in LOSS_INDEXES:
            self.state[next_tile] = 88
            self.state[(current_tile_x, current_tile_y)] = 10
            self.special_things["pacman"] = "dead"

    def move_ghost(self, color):
        ghost_place_x, ghost_place_y = self.special_things[color]
        current_tile = self.special_things[color]
        previous_tile_contained_pill = self.state[current_tile] % 10 == 1
        ghost_code = COLOR_CODES[color]

        if color != "blue":
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

        if random.random() <= PROBABILITIES[color]:
            # manhattan
            random.shuffle(eligible_tiles)
            next_tile = min(eligible_tiles, key=self.manhattan_distance)
        else:
            # random
            next_tile = random.choice(eligible_tiles)

        # movement result
        # next tile is a regular tile (with or without a pill)
        if self.state[next_tile] == 11 or self.state[next_tile] == 10:
            self.state[next_tile] = ghost_code + (self.state[next_tile] % 10)
            self.special_things[color] = next_tile

        # poison
        elif self.state[next_tile] == 77 or self.state[next_tile] == 71:
            if self.state[next_tile] == 77:
                self.state[next_tile] = 10
            else:
                self.state[next_tile] = 11
            del self.special_things[color]

        # ghost got the pacman
        elif self.state[next_tile] == 66:
            self.special_things["pacman"] = "dead"
            self.state[next_tile] = 88

        if current_tile != next_tile:
            if previous_tile_contained_pill:
                self.state[current_tile] = 11
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
        return tuple(state_to_return)

    def evaluate_agent(self):
        for step in range(self.steps):
            action = self.agent.choose_next_action(self.state_to_agent())
            if not is_action_legal(action):
                raise Exception("illegal action!", action, "happened at step number:", step)
            self.change_state_after_action(action)
        return self.accumulated_reward


if __name__ == '__main__':
    problems = (

        ((
            (99, 99, 99),
            (99, 11, 99),
            (99, 66, 99),
            (99, 99, 99)
         ), 10),

        ((
            (99, 99, 99, 99, 99),
            (99, 11, 11, 40, 99),
            (99, 31, 10, 10, 99),
            (99, 11, 11, 11, 99),
            (99, 11, 77, 11, 99),
            (99, 11, 11, 66, 99),
            (99, 99, 99, 99, 99)
        ), 20),

        ((
         (99, 99, 99, 99, 99, 99, 99),
         (99, 11, 11, 66, 11, 11, 99),
         (99, 11, 11, 11, 11, 11, 99),
         (99, 11, 11, 71, 11, 51, 99),
         (99, 11, 11, 11, 11, 11, 99),
         (99, 11, 11, 11, 11, 11, 99),
         (99, 99, 99, 99, 99, 99, 99),
         ), 50)

    )

    results = []

    for problem, num_of_steps in problems:
        my_eval = Evaluator(ex2.PacmanController(problem, num_of_steps), problem, num_of_steps)
        results.append(my_eval.evaluate_agent())

    for number, result in enumerate(results):
        print("the result for input", number + 1, "is", result)

