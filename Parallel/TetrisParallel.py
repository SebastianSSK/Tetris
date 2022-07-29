import random

import pygame

from math import sqrt, ceil

from AI.AI_Agent import Agent
from Tetris_Game.MainGame import Tetris
from Tetris_Game.Settings import *
from Tetris_Game.TetrisUtilities import get_color_tuple


class TetrisParallel:
    def __init__(self, number_of_games: int):
        self.tetris_parallel_model = TetrisParallelModel(number_of_games)
        self.tetris_parallel_view = TetrisParallelView(self.tetris_parallel_model)
        self.tetris_parallel_controller = TetrisParallelController(self.tetris_parallel_model)
        self.run_games()

    def run_games(self):
        pygame.time.set_timer(pygame.USEREVENT + 1, SPEED_DEFAULT)
        pygame.time.set_timer(pygame.USEREVENT + 2, DISPLAY_TEXT_SPEED)
        clock = pygame.time.Clock()
        # while game is running
        while self.tetris_parallel_model.running:
            # draw and update game
            self.tetris_parallel_view.draw()
            self.tetris_parallel_controller.update()
            clock.tick(MAX_FPS)
        pygame.quit()


class TetrisParallelModel:
    def __init__(self, number_of_games: int):
        self.number_of_games = number_of_games

        self.agents = []
        self.tetris_games = []
        self.best_game = 0

        self.running = True
        self.display_best_of_generation = False
        self.current_text_index = 0

        self.high_score = 0
        self.high_score_lines = 0

        self.weight_line_cleared = 0
        self.weight_aggregate_height = 0
        self.weight_holes = 0
        self.weight_bumpiness = 0
        self.mutation_chance = 0
        self.timer = 0

        # get scale based of number of games
        self.number_of_rows = 2 * ceil(sqrt(0.5 * number_of_games))
        self.scale = 2 / self.number_of_rows

        # offset for each game
        self.margin = int(MARGIN * self.scale)
        self.text_x_start = GRID_COL_COUNT * (SCREEN_HEIGHT_ALGORITHM(self.scale) // GRID_ROW_COUNT) + self.margin
        self.text_y_start = SCREEN_HEIGHT_ALGORITHM(self.scale) + self.margin


class TetrisParallelView:
    def __init__(self, tetris_parallel_model: TetrisParallelModel):
        pygame.init()
        pygame.font.init()

        self.screen_width = 2 * SCREEN_WIDTH_ALGORITHM(1) + 2 * MARGIN
        self.screen_height = SCREEN_HEIGHT_ALGORITHM(1) + 2 * MARGIN
        self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height))
        self.display_best_over_all = False

        self.tetris_parallel_model = tetris_parallel_model

        self.x = self.tetris_parallel_model.text_x_start * self.tetris_parallel_model.number_of_rows + MARGIN
        self.y = MARGIN
        self.width = self.screen_width - self.tetris_parallel_model.text_x_start * \
                     self.tetris_parallel_model.number_of_rows - 3 * MARGIN

        # todo change this mess
        number_of_games_in_column = ceil(self.tetris_parallel_model.number_of_games
                                         / self.tetris_parallel_model.number_of_rows)
        game_board_height = (SCREEN_HEIGHT_ALGORITHM(
            self.tetris_parallel_model.scale) // GRID_ROW_COUNT) * GRID_ROW_COUNT

        margin_correction = self.tetris_parallel_model.margin - MARGIN

        self.height = (number_of_games_in_column
                       - 1) * self.tetris_parallel_model.text_y_start + game_board_height + margin_correction

    def draw(self):
        self.screen.fill(get_color_tuple(COLORS.get("BACKGROUND_BLACK")))
        for i in range(self.tetris_parallel_model.number_of_games):
            self.tetris_parallel_model.tetris_games[i].tetris_view.draw()
        self.draw_right_side()
        # update screen
        pygame.display.update()

    def _draw_text_center_x(self, text: str, font_size: int, x: int, y: int, width: int, color_str="WHITE"):
        """:param: text the text that will be displayed
           :param: font_size font size that will be used to display the text
           :param: x x coordinate of the text (left)
           :param: y y coordinates of the text (top)
           :param: width to which the text should be centered
           :param: color_str Color of the text with default white"""
        text_image = pygame.font.SysFont(FONT_NAME, int(font_size)) \
            .render(text, False, get_color_tuple(COLORS[color_str]))

        self.screen.blit(text_image, (x + width // 2 - text_image.get_width() // 2, y))

    def draw_text(self, text: str, font_size: int, x: int, y: int, index: int, color_str="WHITE"):
        text_image = pygame.font.SysFont(FONT_NAME, int(font_size)) \
            .render(text, False, get_color_tuple(COLORS[color_str]))
        self.screen.blit(text_image, (x, y))

    def draw_right_side(self):
        color = get_color_tuple(COLORS.get("PADDING_DARK"))
        pygame.draw.rect(self.screen, color, (self.x, self.y, self.width, self.height), 3, 10)

        self._draw_text_center_x(text="Tetris Parallel", font_size=64, x=self.x, y=self.y, width=self.width)

        if not self.tetris_parallel_model.display_best_of_generation:
            self.tetris_parallel_model.current_text_index = 0
            # get best game
            i = self.tetris_parallel_model.best_game
            # best agent of current generation
            self._draw_text_center_x(text="Best AI-Agent", font_size=32, x=self.x, y=self.y + 96, width=self.width)

            # back up current values
            std_scale = self.tetris_parallel_model.tetris_games[i].tetris_view.game_scale
            std_view_offset_x = self.tetris_parallel_model.tetris_games[i].tetris_view.offset_x
            std_view_offset_y = self.tetris_parallel_model.tetris_games[i].tetris_view.offset_y

            self.tetris_parallel_model.tetris_games[i].tetris_view.set_scale(0.75, 1)
            # center coordinates
            y = self.height + self.y - self.tetris_parallel_model.tetris_games[i].tetris_view.screen_height - MARGIN
            x = self.width // 2 + self.x - self.tetris_parallel_model.tetris_games[i].tetris_view.screen_width // 2
            self.tetris_parallel_model.tetris_games[i].tetris_view.set_offset(x, y)
            self.tetris_parallel_model.tetris_games[i].tetris_view.display_statistics = True
            self.tetris_parallel_model.tetris_games[i].tetris_view.draw()

            self.tetris_parallel_model.tetris_games[i].tetris_view.display_statistics = False
            self.tetris_parallel_model.tetris_games[i].tetris_view.set_scale(std_scale)
            self.tetris_parallel_model.tetris_games[i].tetris_view.set_offset(std_view_offset_x, std_view_offset_y)

        # display data of the best agent of all generations
        else:
            y = self.y + 96
            # best agent of all generations
            self._draw_text_center_x(text="Best AI-Agent over all", font_size=32,
                                     x=self.x, y=y, width=self.width)

            lines_cleared = self.tetris_parallel_model.weight_line_cleared
            aggregate_height = self.tetris_parallel_model.weight_aggregate_height
            weight_holes = self.tetris_parallel_model.weight_holes
            weight_bumpiness = self.tetris_parallel_model.weight_bumpiness
            mutation_chance = self.tetris_parallel_model.mutation_chance

            x = self.x + MARGIN
            y += 64
            self.draw_text(text=f"Weight aggregate height: {aggregate_height:.3f}", font_size=16,
                           x=x, y=y,
                           index=self.tetris_parallel_model.current_text_index)
            y += 32
            self.draw_text(text=f"Weight holes: {weight_holes:.3f}", font_size=16,
                           x=x, y=y,
                           index=self.tetris_parallel_model.current_text_index)
            y += 32
            self.draw_text(text=f"Weight bumpiness: {weight_bumpiness:.3f}", font_size=16,
                           x=x, y=y,
                           index=self.tetris_parallel_model.current_text_index)
            y += 32
            self.draw_text(text=f"Weight lines cleared: {lines_cleared:.3f}", font_size=16,
                           x=x, y=y,
                           index=self.tetris_parallel_model.current_text_index)
            y += 32
            self.draw_text(text=f"Mutation chance: {mutation_chance:.3f}", font_size=16,
                           x=x, y=y,
                           index=self.tetris_parallel_model.current_text_index)

            high_score = self.tetris_parallel_model.high_score
            high_score_lines = self.tetris_parallel_model.high_score_lines

            y += 64
            self.draw_text(text=f"Highest score: {high_score:.3f}", font_size=16,
                           x=x, y=y,
                           index=self.tetris_parallel_model.current_text_index)
            y += 32
            self.draw_text(text=f"Highest number of lines cleared: {high_score_lines}",
                           font_size=16, x=x, y=y,
                           index=self.tetris_parallel_model.current_text_index)


class TetrisParallelController:
    def __init__(self, tetris_parallel_model: TetrisParallelModel):
        self.tetris_parallel_model = tetris_parallel_model

        # map keys to methods
        self.key_actions = {
            "TAB": lambda: self.toggle_display_mode(),
            "c": lambda: self.start_new_round()
        }

        self.generate_games()
        self.generate_agents()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.USEREVENT + 1:
                self.tetris_parallel_model.timer += 1
                self.calculate_agent_moves()
                self.drop()
                # check which game has highest score now
                self.find_best_agent()
                if self.all_games_over():
                    self.tetris_parallel_model.timer = 0
                    self.start_new_round()
            elif event.type == pygame.USEREVENT + 2 and self.tetris_parallel_model.display_best_of_generation:
                self.tetris_parallel_model.current_text_index += 1
            elif event.type == pygame.KEYDOWN and self.tetris_parallel_model.running:
                for key in self.key_actions:
                    if event.key == eval("pygame.K_" + key):
                        self.key_actions[key]()

    def calculate_agent_moves(self):
        for agent in self.tetris_parallel_model.agents:
            agent.calculate_next_move()

    def find_best_agent(self):
        """finds index of game with highest score"""
        index = 0
        current_score = 0
        for i in range(0, len(self.tetris_parallel_model.tetris_games)):
            if self.tetris_parallel_model.tetris_games[i].tetris_model.game_over:
                continue
            score = self.tetris_parallel_model.tetris_games[i].tetris_model.score
            if score > current_score:
                current_score = score
                index = i
        self.tetris_parallel_model.best_game = index

    def generate_games(self):
        number_of_rows = self.tetris_parallel_model.number_of_rows
        board_width = self.tetris_parallel_model.text_x_start
        board_height = self.tetris_parallel_model.text_y_start
        margin = self.tetris_parallel_model.margin
        # generate all games
        for i in range(self.tetris_parallel_model.number_of_games):
            self.tetris_parallel_model.tetris_games.append(
                Tetris(interactive=False,
                       visible=True,
                       offset_x=i % number_of_rows * board_width + margin,
                       offset_y=i // number_of_rows * board_height + margin,
                       display_statistics=False,
                       display_controls=False,
                       title="AI_AGENT {}".format(i),
                       lock_step=True,
                       scale=self.tetris_parallel_model.scale))
        # default best game is game with index zero
        self.tetris_parallel_model.best_game = 0

    def start_new_round(self):

        agents, games = self.tetris_parallel_model.agents, self.tetris_parallel_model.tetris_games
        agents_game_mapping = list(zip(agents, games))
        n = len(agents_game_mapping) // 2
        # sort best agents
        agents_game_mapping = sorted(agents_game_mapping, reverse=True, key=lambda x: x[1].tetris_model.score)[:n]

        if agents_game_mapping[0][1].tetris_model.score > self.tetris_parallel_model.high_score:
            self.update_best_overall_agent(high_score=agents_game_mapping[0][1].tetris_model.score,
                                           high_score_lines=agents_game_mapping[0][1].tetris_model.lines,
                                           weight_line_cleared=agents_game_mapping[0][0].weight_line_cleared,
                                           weight_holes=agents_game_mapping[0][0].weight_holes,
                                           weight_bumpiness=agents_game_mapping[0][0].weight_bumpiness,
                                           weight_aggregate_height=agents_game_mapping[0][0].weight_aggregate_height,
                                           mutation_chance=agents_game_mapping[0][0].mutation_weight)

        for game in self.tetris_parallel_model.tetris_games:
            game.tetris_controller.reset_game()

        # best agent will be part of next generation
        agents_game_mapping[0][0].game = self.tetris_parallel_model.tetris_games[0]

        agents = [agents_game_mapping[0][0]]
        for i in range(1, self.tetris_parallel_model.number_of_games):
            agent_id = random.randint(1, n - 1)
            # every new agent is based on the winner and some other random agent
            agents.append(agents_game_mapping[0][0].get_child(agents_game_mapping[agent_id][0], games[i]))

        self.tetris_parallel_model.agents = agents

    def all_games_over(self):
        return all([game.tetris_model.game_over for game in self.tetris_parallel_model.tetris_games])

    def generate_agents(self):
        for i in range(self.tetris_parallel_model.number_of_games):
            self.tetris_parallel_model.agents.append(Agent(self.tetris_parallel_model.tetris_games[i]))

    def toggle_display_mode(self):
        toggle_value = not self.tetris_parallel_model.display_best_of_generation
        self.tetris_parallel_model.display_best_of_generation = toggle_value

    def drop(self):
        for tetris_game in self.tetris_parallel_model.tetris_games:
            tetris_game.tetris_controller.drop()

    def update_best_overall_agent(self, high_score: int, high_score_lines: int, weight_line_cleared: float,
                                  weight_aggregate_height: float, weight_holes: float, weight_bumpiness: float,
                                  mutation_chance: float):
        self.tetris_parallel_model.high_score = high_score
        self.tetris_parallel_model.high_score_lines = high_score_lines

        self.tetris_parallel_model.weight_line_cleared = weight_line_cleared
        self.tetris_parallel_model.weight_aggregate_height = weight_aggregate_height
        self.tetris_parallel_model.weight_holes = weight_holes
        self.tetris_parallel_model.weight_bumpiness = weight_bumpiness
        self.tetris_parallel_model.mutation_chance = mutation_chance

    def quit(self):
        self.tetris_parallel_model.running = False
