MULTI_SCORE_ALGORITHM = (lambda lines_cleared: 5 ** lines_cleared)
SCREEN_WIDTH_ALGORITHM = (lambda size_scale: int(360 / SCREEN_RATIO * size_scale))
SCREEN_HEIGHT_ALGORITHM = (lambda size_scale: int(720 * size_scale))

PER_STEP_SCORE_GAIN = 0.001

SPEED_DEFAULT = 5  # 750 MS
SPEED_SCALE_ENABLED = True  # game gets faster with more points?
SPEED_SCALE = 0.05  # speed = max(50, 750 - SCORE * SPEED_SCALE)
DISPLAY_PREDICTION = True
HAS_DISPLAY = True

FONT_NAME = "Consolas"

# debug level
MIN_DEBUG_LEVEL = 10

# grid dimensions
GRID_ROW_COUNT = 20
GRID_COL_COUNT = 10

SCREEN_RATIO = 0.55
MAX_FPS = 30

ALWAYS_DRAW = True
STEP_ACTION = True

# "Optimal" fitness function configuration
WEIGHT_AGGREGATE_HEIGHT = -0.3
WEIGHT_HOLES = -0.75
WEIGHT_BUMPINESS = -0.18
WEIGHT_LINE_CLEARED = 1.3

DISPLAY_TEXT_SPEED = 25  # 25 MS
MARGIN = 20

# colors
COLORS = {
    # Display
    "BACKGROUND_BLACK": "000000",
    "BACKGROUND_DARK": "021c2d",
    "BACKGROUND_LIGHT": "00263f",
    "PADDING_DARK": "004211",
    "TRIANGLE_GRAY": "efe6ff",
    "WHITE": "ffffff",
    "RED": "ff0000",
    # Tetris pieces
    "TILE_I": "ffb900",
    "TILE_L": "2753f1",
    "TILE_J": "f7ff00",
    "TILE_S": "ff6728",
    "TILE_Z": "11c5bf",
    "TILE_T": "ae81ff",
    "TILE_O": "e94659",
    # Highlights
    "HIGHLIGHT_GREEN": "22ee22",
    "HIGHLIGHT_RED": "ee2222",
}

MESSAGES = {
    # Display
    "TITLE": "Tetris",
    "CONTROLS": "Left/Right - Move tile\nUp - Rotate tile\nDown - Fast drop\nSpace - Insta-drop\nEscape - Play/Pause\n",
    "HIGH_SCORE": "H.Score: {:.2f} (x{})",
    "SCORE": "Score: {:.2f} (x{})",
    "FITNESS": "Fitness: {:.2f}",
    "SPEED": "Speed: {}ms",
    "NEXT_TILE": "Next tile: {}",
}

# shapes

SHAPES = ['I', 'O', 'T', 'J', 'L', 'S', 'Z']
SHAPES_ID = {'I': 1, 'O': 2, 'T': 3, 'J': 4, 'L': 5, 'S': 6, 'Z': 7}

I_shape = [[1], [1], [1], [1]]

O_shape = [[2, 2], [2, 2]]

T_shape = [[3, 0], [3, 3], [3, 0]]

J_shape = [[0, 0, 4], [4, 4, 4]]

L_shape = [[5, 5, 5], [0, 0, 5]]

S_shape = [[0, 6], [6, 6], [6, 0]]

Z_shape = [[7, 0], [7, 7], [0, 7]]
