from Tetris_Game.Settings import *
from Tetris_Game.Controls import *


class ShapeForms(Enum):
    I_SHAPE = 1
    O_SHAPE = 2
    T_SHAPE = 3
    J_SHAPE = 4
    L_SHAPE = 5
    S_SHAPE = 6
    Z_SHAPE = 7


class Shape:
    def __init__(self, shape_form, board, x, y):
        if shape_form == ShapeForms.I_SHAPE:
            self.shape = I_shape
            self.name = SHAPES[0]
            self.max_number_of_turns = 1
        elif shape_form == ShapeForms.O_SHAPE:
            self.shape = O_shape
            self.name = SHAPES[1]
            self.max_number_of_turns = 0
        elif shape_form == ShapeForms.T_SHAPE:
            self.shape = T_shape
            self.name = SHAPES[2]
            self.max_number_of_turns = 3
        elif shape_form == ShapeForms.J_SHAPE:
            self.shape = J_shape
            self.name = SHAPES[3]
            self.max_number_of_turns = 3
        elif shape_form == ShapeForms.L_SHAPE:
            self.shape = L_shape
            self.name = SHAPES[4]
            self.max_number_of_turns = 3
        elif shape_form == ShapeForms.S_SHAPE:
            self.shape = S_shape
            self.name = SHAPES[5]
            self.max_number_of_turns = 1
        elif shape_form == ShapeForms.Z_SHAPE:
            self.shape = Z_shape
            self.name = SHAPES[6]
            self.max_number_of_turns = 1
        else:
            raise ValueError("Value {} is no valid shape form".format(shape_form))
        self.x = x
        self.y = y
        self.board = board

        self.y_distance_to_collision = -1
        self.placed = False
        self.placeable = True

    def turned(self, direc):
        if direc.value == Turn.RIGHT_TURN.value:
            return list(zip(*self.shape[::-1]))
        elif direc.value == Turn.LEFT_TURN.value:
            return list(zip(*[e[::-1] for e in self.shape]))
        else:
            raise ValueError("Wrong value direction should be {} or {}".format(Turn.LEFT_TURN, Turn.RIGHT_TURN))

    def get_y_distance_to_collision(self):
        """:returns distance to collision from this shape"""
        if self.y_distance_to_collision < 0:
            self.y_distance_to_collision = self.board.distance_to_collision(self.shape, self.x, self.y)
            return self.y_distance_to_collision
        # correct distance is already known
        elif self.y_distance_to_collision > 0:
            return self.y_distance_to_collision
        return 0

    def place_shape(self):
        """place this shape in the board"""
        # check if distance is already known
        if self.y_distance_to_collision < 0:
            self.placeable = self.board.place_shape(self.shape, self.x, self.y)
        else:
            self.placeable = self.board.place_shape(self.shape, self.x, self.y, self.y_distance_to_collision)
        self.placed = self.placeable

    def decrease_y(self):
        if self.placed:
            raise ValueError("shape is already placed and should not decrease y any further")
        # if distance not set, find distance to collision
        if self.y_distance_to_collision < 0:
            self.y_distance_to_collision = self.board.distance_to_collision(self.shape, self.x, self.y)
        # further decrease y
        if self.y_distance_to_collision > 0:
            self.y -= 1
            self.y_distance_to_collision -= 1
        # place ship on board
        else:
            self.place_shape()

    def shift_to_direction(self, direc: Direction):
        """moves shape to direction specified by direct"""
        if direc.value != Direction.LEFT.value and direc.value != Direction.RIGHT.value:
            raise ValueError("direction should be {} or {} not {}".format(Direction.LEFT, Direction.RIGHT, direc))
        if not self.board.has_collision(self.shape, self.x + direc.value, self.y):
            self.x += direc.value
            # distance if know not known
            self.y_distance_to_collision = -1

    def turn_in_direction(self, direc: Turn):
        """
        :returns if shape was turned

        turns shape in direction specified by direct
        """
        potential_shape_structure = self.turned(direc)
        if not self.board.has_collision(potential_shape_structure, self.x, self.y):
            self.shape = potential_shape_structure
            # distance is now unknown
            self.y_distance_to_collision = -1
            return True
        return False
