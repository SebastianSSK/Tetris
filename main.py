import cProfile
import pstats

from Parallel.TetrisParallel import TetrisParallel
from Tetris_Game.MainGame import Tetris

"""
    profiler = cProfile.Profile()
    profiler.enable()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()"""
if __name__ == '__main__':
    TetrisParallel(2 * 49)
    # Tetris(scale=1)
