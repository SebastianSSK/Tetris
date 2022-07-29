from enum import Enum

from Tetris_Game import Board
from Tetris_Game.Controls import Turn, Direction
from Tetris_Game.Settings import *


class ShapeForms(Enum):
    I_SHAPE = 1
    O_SHAPE = 2
    T_SHAPE = 3
    J_SHAPE = 4
    L_SHAPE = 5
    S_SHAPE = 6
    Z_SHAPE = 7

    def __new__(cls, value: int):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value


class Shape:
    def __init__(self, shape_form: ShapeForms, board: Board, x: int, y: int):
        """
        :param shape_form: the form id of the shape
        :param board: the current tetris board
        :param x: x-position of the shape
        :param y: y-position of the shape
        """

        # find the correct shape and saveit as list representation
        if shape_form == ShapeForms.I_SHAPE:
            self.shape = I_shape
            self.name = SHAPE_CHARS[0]
            self.max_number_of_turns = 1
        elif shape_form == ShapeForms.O_SHAPE:
            self.shape = O_shape
            self.name = SHAPE_CHARS[1]
            self.max_number_of_turns = 0
        elif shape_form == ShapeForms.T_SHAPE:
            self.shape = T_shape
            self.name = SHAPE_CHARS[2]
            self.max_number_of_turns = 3
        elif shape_form == ShapeForms.J_SHAPE:
            self.shape = J_shape
            self.name = SHAPE_CHARS[3]
            self.max_number_of_turns = 3
        elif shape_form == ShapeForms.L_SHAPE:
            self.shape = L_shape
            self.name = SHAPE_CHARS[4]
            self.max_number_of_turns = 3
        elif shape_form == ShapeForms.S_SHAPE:
            self.shape = S_shape
            self.name = SHAPE_CHARS[5]
            self.max_number_of_turns = 1
        elif shape_form == ShapeForms.Z_SHAPE:
            self.shape = Z_shape
            self.name = SHAPE_CHARS[6]
            self.max_number_of_turns = 1
        else:
            raise ValueError("Value {} is no valid shape form".format(shape_form))
        # initial position
        self.x = x
        self.y = y
        self.board = board

        # current distance to collisions is not known
        self.y_distance_to_collision = -1
        self.placed = False

    def turned(self, direction) -> list:
        """
        :param direction: the direction to which the shape should be turned
        :return: turned list representation of the shape
        """
        # check if direction is right or left
        if direction.value == Turn.RIGHT_TURN.value:
            # return right turned list representation of the shape
            return list(zip(*self.shape[::-1]))
        elif direction.value == Turn.LEFT_TURN.value:
            # return left turned list representation of the shape
            return list(zip(*[e[::-1] for e in self.shape]))
        else:
            # given direction was not valid
            raise ValueError("Wrong value direction should be {} or {}".format(Turn.LEFT_TURN, Turn.RIGHT_TURN))

    def get_y_distance_to_collision(self) -> int:
        """
        finds the distance until the shape collides with something (placed shape or bottom of board)

        :return: distance to collision from this shape
        """
        if self.y_distance_to_collision == -1:
            self.y_distance_to_collision = self.board.distance_to_collision(self.shape, self.x, self.y)
            return self.y_distance_to_collision
        # correct distance is already known
        return self.y_distance_to_collision

    def place_shape(self):
        """
        place this shape in the board
        """
        # check if distance is already known
        if self.y_distance_to_collision == -1:
            self.placed = self.board.place_shape(self.shape, self.x, self.y)
        else:
            self.placed = self.board.place_shape(self.shape, self.x, self.y, self.y_distance_to_collision)

    def decrease_y(self):
        """
        decrease the y-value of the shape by one, if possible.
        if it is not possible the shape is placed
        """
        if self.placed: raise ValueError("shape is already placed and should not decrease y any further")
        # if distance not set, find distance to collision
        if self.y_distance_to_collision == -1:
            self.y_distance_to_collision = self.board.distance_to_collision(self.shape, self.x, self.y)
        # check if shape is already at bottom
        if self.y_distance_to_collision <= 0:
            # place shape on board
            self.place_shape()
            return
        # further decrease y
        self.y -= 1
        self.y_distance_to_collision -= 1

    def shift_to_direction(self, direction: Direction) -> bool:
        """
        shifts the shape left or right
        :param direction: direction of the shift
        :return: if shape was shifted
        """
        # make sure direction value is valid
        if direction.value != Direction.LEFT.value and direction.value != Direction.RIGHT.value:
            raise ValueError("direction should be {} or {} not {}".format(Direction.LEFT, Direction.RIGHT, direction))
        # check if shift is possible
        if self.board.has_collision(self.shape, self.x + direction.value, self.y): return False
        # change the position of the shape
        self.x += direction.value
        # distance is set to not known
        self.y_distance_to_collision = -1

        return True

    def turn_in_direction(self, direction: Turn) -> bool:
        """
        turns shape in direction specified by direction
        @:param direction: direction to which the shape is turned
        :returns if shape was turned
        """
        # check how shape would look after turn
        potential_shape_structure = self.turned(direction)
        # check if new shape would have collision
        if self.board.has_collision(potential_shape_structure, self.x, self.y): return False
        # -> shape can be turned safely
        self.shape = potential_shape_structure
        # distance is set to not known
        self.y_distance_to_collision = -1
        return True
