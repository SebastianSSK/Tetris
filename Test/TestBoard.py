import unittest

from Tetris_Game.Board import TetrisBoard
from Tetris_Game.Controls import Turn
from Tetris_Game.Settings import *
from Tetris_Game.Shape import Shape, ShapeForms


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.board = TetrisBoard()

    def test_distance_to_collision_I_shape(self):
        self.assertEqual(20, self.board.distance_to_collision(I_shape, 0, 20))
        self.assertEqual(16, self.board.distance_to_collision(I_shape, 3, 16))
        self.assertEqual(14, self.board.distance_to_collision(I_shape, 6, 14))
        self.assertRaises(OverflowError, lambda: self.board.distance_to_collision(I_shape, 5, 21))

    def test_distance_to_collision_O_shape(self):
        self.assertEqual(9, self.board.distance_to_collision(O_shape, 0, 10))
        self.assertEqual(8, self.board.distance_to_collision(O_shape, 3, 9))
        self.assertEqual(19, self.board.distance_to_collision(O_shape, 8, 20))
        self.assertRaises(OverflowError, lambda: self.board.distance_to_collision(O_shape, 8, 21))

    def test_distance_to_collision_T_shape(self):
        self.assertEqual(19, self.board.distance_to_collision(T_shape, 0, 20))
        self.assertEqual(15, self.board.distance_to_collision(T_shape, 3, 16))
        self.assertEqual(13, self.board.distance_to_collision(T_shape, 7, 14))
        self.assertEqual(-2, self.board.distance_to_collision(T_shape, 5, -1))
        self.assertRaises(OverflowError, lambda: self.board.distance_to_collision(T_shape, 5, 22))

    def test_distance_to_collision_J_shape(self):
        self.assertEqual(18, self.board.distance_to_collision(J_shape, 0, 20))
        self.assertEqual(14, self.board.distance_to_collision(J_shape, 3, 16))
        self.assertEqual(12, self.board.distance_to_collision(J_shape, 6, 14))
        self.assertRaises(OverflowError, lambda: self.board.distance_to_collision(J_shape, 9, 21))

    def test_place_shape(self):
        # add I shape to board
        self.board.place_shape(I_shape, 0, 16)
        self.assertEqual(SHAPES_ID['I'], self.board.column_list[0].column[0])
        self.assertEqual(SHAPES_ID['I'], self.board.column_list[1].column[0])
        self.assertEqual(SHAPES_ID['I'], self.board.column_list[2].column[0])
        self.assertEqual(SHAPES_ID['I'], self.board.column_list[3].column[0])

        # add Z shape to board
        self.board.place_shape(Z_shape, 0, 20)
        self.assertEqual(0, self.board.column_list[0].column[1])
        self.assertEqual(SHAPES_ID['Z'], self.board.column_list[0].column[2])

        self.assertEqual(SHAPES_ID['Z'], self.board.column_list[1].column[1])
        self.assertEqual(SHAPES_ID['Z'], self.board.column_list[1].column[2])

        self.assertEqual(SHAPES_ID['Z'], self.board.column_list[2].column[1])
        self.assertEqual(0, self.board.column_list[2].column[2])

        self.assertEqual(0, self.board.column_list[3].column[1])
        self.assertEqual(0, self.board.column_list[3].column[2])

    def test_remove_full_rows(self):
        self.board.place_shape(I_shape, 0, 20)
        self.board.place_shape(I_shape, 4, 20)
        # L shape turned two times
        shape = Shape(ShapeForms.L_SHAPE, self.board, 5, 15)
        shape.turn_in_direction(Turn.LEFT_TURN)
        shape.turn_in_direction(Turn.LEFT_TURN)
        self.board.place_shape(shape.shape, 7, 20)

        self.board.place_shape(I_shape, 3, 20)
        # J shape turned one time left turned
        shape = Shape(ShapeForms.J_SHAPE, self.board, 5, 15)
        shape.turn_in_direction(Turn.LEFT_TURN)
        self.board.place_shape(shape.shape, 0, 20)

        # L shape turned one time right turned
        shape = Shape(ShapeForms.L_SHAPE, self.board, 5, 15)
        shape.turn_in_direction(Turn.RIGHT_TURN)
        self.board.place_shape(shape.shape, 1, 20)

        # J shape turned one time left turned
        shape = Shape(ShapeForms.J_SHAPE, self.board, 5, 15)
        shape.turn_in_direction(Turn.LEFT_TURN)
        self.board.place_shape(shape.shape, 4, 20)

        # I shape turned one time left turned
        shape = Shape(ShapeForms.I_SHAPE, self.board, 5, 15)
        shape.turn_in_direction(Turn.LEFT_TURN)
        self.board.place_shape(shape.shape, 9, 20)

        self.board.remove_full_rows()

        self.assertNotEqual(0, self.board.column_list[0].column[0])
        self.assertNotEqual(0, self.board.column_list[1].column[0])
        self.assertNotEqual(0, self.board.column_list[2].column[0])
        self.assertNotEqual(0, self.board.column_list[3].column[0])
        self.assertNotEqual(0, self.board.column_list[4].column[0])
        self.assertNotEqual(0, self.board.column_list[5].column[0])
        self.assertNotEqual(0, self.board.column_list[6].column[0])
        self.assertEqual(0, self.board.column_list[7].column[0])
        self.assertNotEqual(0, self.board.column_list[8].column[0])
        self.assertNotEqual(0, self.board.column_list[9].column[0])

        self.assertEqual(0, self.board.column_list[0].column[1])
        self.assertEqual(0, self.board.column_list[1].column[1])
        self.assertEqual(0, self.board.column_list[2].column[1])
        self.assertNotEqual(0, self.board.column_list[3].column[1])
        self.assertNotEqual(0, self.board.column_list[4].column[1])
        self.assertEqual(0, self.board.column_list[5].column[1])
        self.assertEqual(0, self.board.column_list[6].column[1])
        self.assertEqual(0, self.board.column_list[7].column[1])
        self.assertEqual(0, self.board.column_list[8].column[1])
        self.assertNotEqual(0, self.board.column_list[9].column[1])

        self.assertTrue(all([column.max_height == -1 or column.column[column.max_height] != 0
                             for column in self.board.column_list]))


if __name__ == '__main__':
    unittest.main()
