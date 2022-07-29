from Tetris_Game.Settings import *


def get_fitness_score(board, score_count):
    score = WEIGHT_LINE_CLEARED * score_count
    score += WEIGHT_AGGREGATE_HEIGHT * sum(board.get_col_heights())
    score += WEIGHT_HOLES * board.get_hole_count()
    score += WEIGHT_BUMPINESS * board.get_bumpiness()
    return score


def get_color_tuple(color_hex="11c5bf"):
    color_hex_temp = color_hex.replace("#", "")
    return tuple(int(color_hex_temp[i:i + 2], 16) for i in (0, 2, 4))
