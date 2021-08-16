import math
import random

from Tetris_Game.Controls import Turn, Direction
from Tetris_Game.MainGame import Tetris
from Tetris_Game.Settings import GRID_ROW_COUNT, GRID_COL_COUNT


class Agent:
    def __init__(self, game: Tetris):
        self.game = game

        self.one_turn = ['O']
        self.two_turns = ['I', 'S', 'Z']
        self.four_turns = ['T', 'L', 'J']

        self.weight_line_cleared = 2 * random.random() - 1
        self.weight_aggregate_height = 2 * random.random() - 1
        self.weight_holes = 2 * random.random() - 1
        self.weight_bumpiness = 2 * random.random() - 1
        self.mutation_chance = random.random()

    def set_weights(self, weight_line_cleared, weight_aggregate_height, weight_holes,
                    weight_bumpiness, mutation_chance):
        self.weight_line_cleared = weight_line_cleared
        self.weight_aggregate_height = weight_aggregate_height
        self.weight_holes = weight_holes
        self.weight_bumpiness = weight_bumpiness
        self.mutation_chance = mutation_chance

    def _weight_position(self, lines_cleared, height_sum, hole_count, bumpiness):
        score = self.weight_line_cleared * lines_cleared**5
        score += self.weight_aggregate_height * height_sum
        score += self.weight_holes * hole_count
        score += self.weight_bumpiness * bumpiness
        return score

    def _evaluate_every_position(self, turns: int):
        # get game board
        board = self.game.tetris_model.game_board
        # get current shape that needs to be placed
        current_shape = self.game.tetris_model.get_current_shape()

        # best move until now
        best_move = {"turn": 0,
                     "move": 0,
                     "score": -math.inf
                     }
        # every turn
        for i in range(turns):
            # for every position shape can be placed
            for x in range(0, GRID_COL_COUNT - len(current_shape.shape) + 1):
                val = board.evaluate_position(current_shape.shape, x, current_shape.y)
                if not val["valid"]:
                    continue
                # score if the shape would be placed at the current position
                score = self._weight_position(val["lines_cleared"],
                                              val["max_heights"],
                                              val["number_of_holes"],
                                              val["bumpiness"])
                # test if current score is better then best score
                if score > best_move["score"]:
                    best_move["turn"] = i
                    best_move["move"] = x - current_shape.x
                    best_move["score"] = score

            # turn shape back to starting position
            current_shape.shape = current_shape.turned(Turn.LEFT_TURN)

        return best_move

    def calculate_next_move(self):
        # get current shape that needs to be placed
        current_shape = self.game.tetris_model.get_current_shape()

        # find best move
        if current_shape.name in self.one_turn:
            next_move = self._evaluate_every_position(1)
        elif current_shape.name in self.two_turns:
            next_move = self._evaluate_every_position(2)
        else:
            next_move = self._evaluate_every_position(4)

        # execute best move
        for i in range(next_move["turn"]):
            self.game.tetris_controller.rotate_tile(Turn.LEFT_TURN)

        direc = Direction.LEFT if next_move["move"] < 0 else Direction.RIGHT

        for i in range(abs(next_move["move"])):
            self.game.tetris_controller.move_shape(direc)

        # self.game.tetris_controller.drop(True)

    def mutate_value(self, value: float):
        sign = 1 if random.random() > 0.5 else -1
        if self.mutation_chance > random.random():
            return (value + sign * self.mutation_chance) / 2
        return value

    def get_mutation_value(self, agent, value_1, value_2):
        return self.mutate_value(value_1) if random.random() < 0.5 else agent.mutate_value(value_2)

    def get_child(self, agent, game):
        weight_holes = self.get_mutation_value(agent, self.weight_holes, agent.weight_holes)

        weight_bumpiness = self.get_mutation_value(agent, self.weight_bumpiness, agent.weight_bumpiness)

        weight_line_cleared = self.get_mutation_value(agent, self.weight_line_cleared, agent.weight_line_cleared)

        weight_aggregate_height = self.get_mutation_value(agent, self.weight_aggregate_height,
                                                          agent.weight_aggregate_height)

        mutation_chance = self.get_mutation_value(agent, self.mutation_chance, agent.mutation_chance)

        result_agent = Agent(game)
        result_agent.set_weights(weight_line_cleared=weight_line_cleared,
                                 weight_aggregate_height=weight_aggregate_height,
                                 weight_bumpiness=weight_bumpiness,
                                 weight_holes=weight_holes,
                                 mutation_chance=mutation_chance)
        return result_agent
