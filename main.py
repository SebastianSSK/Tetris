import cProfile
import pstats

from Parallel.TetrisParallel import TetrisParallel
from Tetris_Game.MainGame import Tetris
from Tetris_Game.Settings import I_shape

"""
    profiler = cProfile.Profile()
    profiler.enable()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()"""
if __name__ == '__main__':

    TetrisParallel(2*4)

    # Tetris(scale=1)