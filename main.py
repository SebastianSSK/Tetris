import cProfile
import pstats

from Parallel.TetrisParallel import TetrisParallel
from Tetris_Game.MainGame import Tetris
from Tetris_Game.Settings import I_shape, SPEED_DEFAULT

if __name__ == '__main__':
    TetrisParallel(2 * 4)
    # Tetris(scale=1.0)
