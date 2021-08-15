import sys
from datetime import *

import pygame as pygame

from Tetris_Game import TetrisUtilities
from Tetris_Game.Board import TetrisBoard
from Tetris_Game.Controls import Direction, Turn
from Tetris_Game.Settings import *
from Tetris_Game.Shape import Shape, ShapeForms
import random


class Tetris:
    def __init__(self, interactive=True, visible=True, offset_x=0, offset_y=0, display_statistics=True,
                 display_controls=True, title="Tetris", lock_step=False, scale=1):
        self.tetris_model = TetrisModel(interactive, visible)
        self.tetris_view = TetrisView(tetris_model=self.tetris_model,
                                      offset_x=offset_x,
                                      offset_y=offset_y,
                                      display_statistics=display_statistics,
                                      display_controls=display_controls,
                                      title=title,
                                      scale=scale)
        self.tetris_controller = TetrisControl(self.tetris_model)
        # if tetris game is ony game run it can execute its own game loop and occupy the main thread
        if not lock_step:
            self.start()

    def start(self):
        """start game loop"""
        self.tetris_model.running = True
        self.tetris_model.paused = False

        pygame.time.set_timer(pygame.USEREVENT + 1, SPEED_DEFAULT if not SPEED_SCALE_ENABLED else int(
            max(50, SPEED_DEFAULT - self.tetris_model.score * SPEED_SCALE)))
        clock = pygame.time.Clock()

        # run game loop
        self.run(clock)

    def run(self, clock):
        """run game loop"""
        while self.tetris_model.running:
            # Game control: step or auto?
            if STEP_ACTION:
                self.tetris_controller.update()
            # Drawing of the UI
            if not STEP_ACTION or ALWAYS_DRAW:
                self.tetris_view.draw()
            clock.tick(MAX_FPS)
        # exits application
        pygame.quit()

    def get_game_width(self):
        return self.tetris_view.offset_x


class TetrisModel:
    def __init__(self, interactive: bool, visible: bool):
        self.interactive = interactive
        self.visible = visible

        self.game_board = TetrisBoard()

        self.shapes = []

        self.paused = False
        self.game_over = False
        self.running = True

        self.score = 0
        self.lines = 0
        self.fitness = 0
        self.high_score = 0
        self.high_score_lines = 0

        self.on_score_changed_callbacks = []

    # GETTERS
    def get_next_shape(self):
        return self.shapes[len(self.shapes) - 2]

    def get_current_shape(self):
        """get current shape"""
        # if no shape is left, generate new shapes
        return self.shapes[len(self.shapes) - 1]


class TetrisView:
    def __init__(self, tetris_model: TetrisModel, offset_x=0, offset_y=0, display_statistics=True,
                 display_controls=True, title="Tetris", scale=1):
        log("Initializing system...", 3)
        self.tetris_model = tetris_model

        self.title = title
        # should display score, fitness, etc.
        self.display_statistics = display_statistics
        # should display controls
        self.display_controls = display_controls
        self.color_hash = {}

        self.offset_x = offset_x
        self.offset_y = offset_y

        # set text scale and game scale
        self.game_scale = scale
        self.text_scale = scale
        # set screen dimensions
        self.screen_width = SCREEN_WIDTH_ALGORITHM(self.game_scale)
        self.screen_height = SCREEN_HEIGHT_ALGORITHM(self.game_scale)

        self.grid_size = self.screen_height // GRID_ROW_COUNT
        # correct height to multiple of gid size
        self.screen_height = self.grid_size * GRID_ROW_COUNT
        log("Tetris grid size calculated to: {}".format(self.grid_size), 2)

        # Coordinates calculations
        self.margin = MARGIN * self.game_scale
        self.text_x_start = GRID_COL_COUNT * self.grid_size + self.margin
        self.text_y_start = self.margin

        # if pygame is not initialized
        if not pygame.get_init():
            self.master = True
            pygame.init()
            pygame.font.init()
            # PyGame configurations
            pygame.event.set_blocked(pygame.MOUSEMOTION)
            if display_statistics:
                # width is large enough to display data
                self.screen = pygame.display.set_mode(size=(
                    self.screen_width,
                    self.screen_height))
            else:
                # only width for game no width for displaying any data
                self.screen = pygame.display.set_mode(size=(
                    GRID_COL_COUNT * self.grid_size,
                    self.screen_height))
        else:
            self.master = False
            self.screen = pygame.display.get_surface()
        log("Screen size set to: ({}, {})".format(self.screen_width, self.screen_height), 2)
        self.obs_size = GRID_ROW_COUNT * GRID_COL_COUNT

    # SETTER
    def set_scale(self, scale, text_scale=None):
        self.game_scale = scale
        self.text_scale = scale if text_scale is None else text_scale
        # set screen dimensions
        self.screen_width = SCREEN_WIDTH_ALGORITHM(self.game_scale)
        self.screen_height = SCREEN_HEIGHT_ALGORITHM(self.game_scale)

        self.grid_size = self.screen_height // GRID_ROW_COUNT
        # correct height to multiple of gid size
        self.screen_height = self.grid_size * GRID_ROW_COUNT

        # Coordinates calculations
        self.margin = MARGIN * self.game_scale
        self.text_x_start = GRID_COL_COUNT * self.grid_size + self.margin
        self.text_y_start = self.margin

    def set_Title(self, title: str):
        self.title = title

    def set_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def get_color_tuple(self, color_hex="11c5bf"):
        if color_hex not in self.color_hash:
            self.color_hash[color_hex] = TetrisUtilities.get_color_tuple(color_hex)
        return self.color_hash[color_hex]

    def draw(self):
        # do not draw if not visible
        if not self.tetris_model.visible:
            return

        ################
        # Tetris Board #
        ################
        # Layered background layer
        n = self.grid_size * GRID_ROW_COUNT
        padding = self.screen_height - n
        for a in range(GRID_COL_COUNT):
            color = self.get_color_tuple(COLORS.get("BACKGROUND_DARK" if a % 2 == 0 else "BACKGROUND_LIGHT"))
            pygame.draw.rect(self.screen, color,
                             (a * self.grid_size + self.offset_x, self.offset_y,
                              self.grid_size, n))  # x,  y, width, height

        if self.tetris_model.game_over:
            self.draw_game_over()
            return

        # Tetris (tile) layer
        # Draw board first
        self.draw_board()

        # Draw hypothesized shape
        if DISPLAY_PREDICTION:
            self.draw_shape(True)
        # Draw current shape
        self.draw_shape()

        if self.display_statistics:
            self.draw_statistics()
        # only if view initialized screen it will update the screen
        if self.master:
            pygame.display.update()

    def draw_text(self, text: str, font_size: int, x: int, y: int, color_str="WHITE"):
        text_image = pygame.font.SysFont(FONT_NAME, int(font_size * self.text_scale)) \
            .render(text, False, self.get_color_tuple(COLORS[color_str]))
        self.screen.blit(text_image, (x + self.offset_x, y + self.offset_y))

    def draw_text_central(self, text: str, font_size: int, x: int, y: int, width: int, color_str="WHITE"):
        text_image = pygame.font.SysFont(FONT_NAME, int(font_size * self.text_scale)) \
            .render(text, False, self.get_color_tuple(COLORS[color_str]))
        self.screen.blit(text_image, (x + self.offset_x + width // 2 - text_image.get_width(),
                                      y + self.offset_y))

    def draw_game_over(self):
        self.draw_text_central(text="GAME OVER", font_size=64,
                               x=self.margin, y=self.screen_height // 2,
                               width=self.screen_width,
                               color_str="BACKGROUND_BLACK")

    def draw_statistics(self):
        #################
        # Message Board #
        #################

        # Coordinates calculations
        text_x_start = self.text_x_start
        text_y_start = self.text_y_start

        # Background layer
        pygame.draw.rect(self.screen,
                         self.get_color_tuple(COLORS.get("BACKGROUND_BLACK")),
                         (text_x_start - self.margin + self.offset_x,
                          self.offset_y,
                          self.screen_width - text_x_start,
                          self.screen_height))

        # Title
        message = self.title
        if self.tetris_model.game_over:
            message = "Game Over"
        elif self.tetris_model.paused:
            message = "= PAUSED ="

        self.draw_text(text=message, font_size=32, x=text_x_start, y=text_y_start)
        text_y_start = 60 * self.text_scale

        # if controls should be displayed
        if self.display_controls:
            # Controls
            for msg in MESSAGES.get("CONTROLS").split("\n"):
                self.draw_text(text=msg, font_size=16, x=text_x_start, y=text_y_start)
                text_y_start += 20 * self.text_scale
            text_y_start += 10 * self.text_scale

        # Score
        score_text = MESSAGES.get("SCORE").format(self.tetris_model.score, self.tetris_model.lines)
        self.draw_text(text=score_text, font_size=16, x=text_x_start, y=text_y_start)
        text_y_start += 30 * self.text_scale

        # High Score
        high_score = self.tetris_model.score if self.tetris_model.score > self.tetris_model.high_score \
            else self.tetris_model.high_score
        high_score_lines = self.tetris_model.lines if self.tetris_model.lines > self.tetris_model.high_score_lines \
            else self.tetris_model.high_score_lines
        high_score_text = MESSAGES.get("HIGH_SCORE").format(high_score, high_score_lines)

        self.draw_text(text=high_score_text, font_size=16, x=text_x_start, y=text_y_start)
        text_y_start += 30 * self.text_scale

        # Fitness score
        fitness_text = MESSAGES.get("FITNESS").format(self.tetris_model.fitness)
        self.draw_text(text=fitness_text, font_size=16, x=text_x_start, y=text_y_start)
        text_y_start += 30 * self.text_scale

        # Speed
        speed = SPEED_DEFAULT if not SPEED_SCALE_ENABLED else \
            int(max(50, SPEED_DEFAULT - self.tetris_model.score * SPEED_SCALE))
        speed_text = text = MESSAGES.get("SPEED").format(speed)
        self.draw_text(speed_text, font_size=16, x=text_x_start, y=text_y_start)
        text_y_start += 30 * self.text_scale

        # Next tile
        next_tile_text = MESSAGES.get("NEXT_TILE").format(self.tetris_model.get_next_shape().name)
        self.draw_text(next_tile_text, font_size=16, x=text_x_start, y=text_y_start)
        text_y_start += 30 * self.text_scale

        self.draw_next_shape((text_x_start, text_y_start))

    def draw_board(self):
        """draws current board with all placed shapes to the screen"""
        # list of all columns
        column_list = self.tetris_model.game_board.column_list
        # for every position
        for x in range(len(column_list)):
            for y in range(GRID_ROW_COUNT):
                # shape value
                val = column_list[x].column[y]
                if val == 0:
                    continue
                coordinate_x = self.grid_size * x
                coordinate_y = (GRID_ROW_COUNT - y - 1) * self.grid_size
                self._draw_shape(coordinate_x, coordinate_y, val)

    def draw_shape(self, outline_only=False):
        """ :param outline_only if true only the outline will be visible
        draws current shape to screen"""
        # get current shape
        shape = self.tetris_model.get_current_shape()
        offset_y = shape.get_y_distance_to_collision() if outline_only else 0
        # for all shape positions
        for rel_x, line in enumerate(shape.shape):
            for rel_y, val in enumerate(line):
                if val == 0:
                    continue
                x = (shape.x + rel_x) * self.grid_size
                y = (GRID_ROW_COUNT - shape.y - 1 + rel_y + offset_y) * self.grid_size
                self._draw_shape(x, y, val, outline_only)

    def draw_next_shape(self, pos):
        next_shape = self.tetris_model.get_next_shape()
        for rel_x, line in enumerate(next_shape.shape):
            for rel_y, val in enumerate(line):
                if val == 0:
                    continue
                x = pos[0] + rel_x * self.grid_size
                y = pos[1] + rel_y * self.grid_size
                self._draw_shape(x, y, val)

    def _draw_shape(self, x, y, val, outline_only=False):
        if outline_only:
            # Outline-only for prediction location
            pygame.draw.rect(self.screen,
                             self.get_color_tuple(COLORS.get("TILE_" + SHAPES[val - 1])),
                             (x + 1 + self.offset_x,
                              y + 1 + self.offset_y, self.grid_size - 2,
                              self.grid_size - 2),
                             1)
        else:
            pygame.draw.rect(self.screen,
                             self.get_color_tuple(COLORS.get("TILE_" + SHAPES[val - 1])),
                             (x + self.offset_x,
                              y + self.offset_y,
                              self.grid_size,
                              self.grid_size))
            pygame.draw.rect(self.screen,
                             self.get_color_tuple(COLORS.get("BACKGROUND_BLACK")),
                             (x + self.offset_x,
                              y + self.offset_y,
                              self.grid_size,
                              self.grid_size),
                             1)
            # Draw highlight triangle
            offset = int(self.grid_size / 10)
            pygame.draw.polygon(self.screen, self.get_color_tuple(COLORS.get("TRIANGLE_GRAY")),
                                ((x + offset + self.offset_x, y + offset + self.offset_y),
                                 (x + 3 * offset + self.offset_x, y + offset + self.offset_y),
                                 (x + offset + self.offset_x, y + 3 * offset + self.offset_y)))


class TetrisControl:
    def __init__(self, tetris_model: TetrisModel):
        self.tetris_model = tetris_model

        # map keys to methods
        self.key_actions = {
            "ESCAPE": self.toggle_pause,
            "LEFT": lambda: self.move_shape(Direction.LEFT),
            "RIGHT": lambda: self.move_shape(Direction.RIGHT),
            "DOWN": lambda: self.drop(False),
            "SPACE": lambda: self.drop(True),
            "UP": lambda: self.rotate_tile(Turn.LEFT_TURN),
            "r": lambda: self.rotate_tile(Turn.RIGHT_TURN)
        }

        self.generate_shapes()

    def generate_shapes(self):
        """generate list containing all shapes exactly twice and
        shuffle it"""
        list_of_shape_forms = list(ShapeForms) + list(ShapeForms)
        random.shuffle(list_of_shape_forms)
        list_of_shapes = [Shape(shape_form, self.tetris_model.game_board, GRID_COL_COUNT // 2,
                                GRID_ROW_COUNT - 1) for shape_form in list_of_shape_forms]
        self.tetris_model.shapes = list_of_shapes + self.tetris_model.shapes

    def pop_current_shape(self):
        """remove current shape from list"""
        if len(self.tetris_model.shapes) < 3:
            self.generate_shapes()
        self.tetris_model.shapes.pop()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.USEREVENT + 1 and not self.tetris_model.game_over:
                self.drop()
            elif event.type == pygame.KEYDOWN and not self.tetris_model.game_over and self.tetris_model.interactive:
                for key in self.key_actions:
                    if event.key == eval("pygame.K_" + key):
                        self.key_actions[key]()

    def calculate_scores(self):
        score_count = self.tetris_model.game_board.remove_full_rows()

        # Calculate fitness score
        self.tetris_model.fitness = TetrisUtilities.get_fitness_score(self.tetris_model.game_board, score_count)
        # If cleared nothing, early return
        if score_count == 0:
            return
        # Calculate total score based on algorithm
        total_score = MULTI_SCORE_ALGORITHM(score_count)
        # Callback
        for callback in self.tetris_model.on_score_changed_callbacks:
            callback(self.tetris_model.score, self.tetris_model.score + total_score)

        self.tetris_model.score += total_score
        self.tetris_model.lines += score_count
        log("Cleared {} row{} with score {}".format(score_count, 's' if score_count > 1 else '', total_score), 3)
        # Calculate game speed
        if self.tetris_model.interactive:
            pygame.time.set_timer(pygame.USEREVENT + 1, SPEED_DEFAULT if not SPEED_SCALE_ENABLED else int(
                max(25, SPEED_DEFAULT - self.tetris_model.score * SPEED_SCALE)))

    def reset_game(self):
        self.tetris_model.game_board.clear()
        self.tetris_model.shapes.clear()
        self.generate_shapes()
        self.tetris_model.game_over = False

        self.tetris_model.high_score = self.tetris_model.score
        self.tetris_model.high_score_lines = self.tetris_model.lines
        self.tetris_model.score = 0
        self.tetris_model.lines = 0
        self.tetris_model.fitness = 0

    # GAME CONTROL METHODS
    def toggle_pause(self):
        """set paused of tetris model to true"""
        self.tetris_model = True

    def move_shape(self, direc):
        """
        :param direc direction to which the shape is moved
        moves shape left or right
        """
        self.tetris_model.get_current_shape().shift_to_direction(direc)

    def _drop(self, prev_y):
        # y coordinate was not changed -> shape can not be placed
        if not self.tetris_model.get_current_shape().placed and prev_y == self.tetris_model.get_current_shape().y:
            self.tetris_model.game_over = True
        # shape was placed
        elif self.tetris_model.get_current_shape().placed:
            self.tetris_model.score += PER_STEP_SCORE_GAIN * (self.tetris_model.get_current_shape().y - prev_y)
            # remove current shape from list
            self.pop_current_shape()
            self.calculate_scores()
        # y value has changed
        else:
            self.tetris_model.score += PER_STEP_SCORE_GAIN

    def drop(self, instant=False):
        """
        :param instant if true shape will be placed instantly
        if false decreases y coordinate of shape if instant is false
        """
        y = self.tetris_model.get_current_shape().y
        if instant:
            self.tetris_model.get_current_shape().place_shape()
            self._drop(y)
        else:
            self.tetris_model.get_current_shape().decrease_y()
            # if shape is placed remove it from list
            self._drop(y)

    def rotate_tile(self, direc):
        """
        :param direc direction in which the shape is turned
        turn shapes clockwise or counter clockwise
        """
        self.tetris_model.get_current_shape().turn_in_direction(direc)

    def quit(self):
        self.tetris_model.running = False


def log(message, level):
    if MIN_DEBUG_LEVEL > level:
        return
    current_time = datetime.now().strftime("%H:%M:%S:%f")[:-3]
    print(f"[{level}] {current_time} >> {message}")
