import search
import random
import math


ids = ["111111111", "111111111"]


class PacmanProblem(search.Problem):
    """This class implements a spaceship problem"""
    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        search.Problem.__init__(self, initial)
        
    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

    """Feel free to add your own functions"""


def create_pacman_problem(game):
    return PacmanProblem(game)

