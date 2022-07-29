from Tetris_Game.Settings import *


def get_color_tuple(color_hex="11c5bf"):
    color_hex_temp = color_hex.replace("#", "")
    return tuple(int(color_hex_temp[i:i + 2], 16) for i in (0, 2, 4))
