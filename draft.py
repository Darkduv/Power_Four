"""
Credits: code found online
"""

import numpy as np
import pygame
import sys
import math

from typing import Tuple


BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

NB_IN_A_ROW = 4

COLOR_PLAYERS = [BLACK, RED, YELLOW]
GRID_COLOR = BLUE
BACKGROUND_COLOR = BLACK

SQUARE_SIZE = 100
RADIUS = SQUARE_SIZE // 2 - 5

SIZE_FONT = 75
NAME_FONT = "monospace"

NB_PLAYERS = 2


class InvalidMoveError(Exception):
    """Custom error for invalid moves."""


class NotSetUpError(Exception):
    """Custom error raised when accessing something that is not set up."""


class Grid:
    """Stores the grid of power four"""

    def __init__(self, nb_rows: int = 6,
                 nb_cols: int = 7):
        self.board = np.zeros((nb_rows, nb_cols), dtype=int)
        self.nb_rows = nb_rows
        self.nb_cols = nb_cols

    def reset_board(self):
        self.board[:, :] = 0

    def is_valid_location(self, col: int) -> bool:
        """Checks if a column is a valid location for a piece."""
        return self.board[self.nb_rows - 1, col] == 0

    def get_next_open_row(self, col: int) -> int:
        """Finds the first row where a new piece can go.

        This row must be a valid location"""
        for r in range(self.nb_rows):
            if self.board[r, col] == 0:
                return r
        raise InvalidMoveError("This column is filled. Please try another.")

    def drop_piece(self, col: int, id_player: int):
        """Drop the piece in the column."""
        row = self.get_next_open_row(col)
        self.board[row, col] = id_player

    def print_board(self):
        print(np.flip(self.board, 0))

    @staticmethod
    def index_diag_slope(length):
        """Gives the index used to extract a diagonal from the board"""
        r1_diag_slope = np.arange(length)
        r2_diag_slope = length - 1 - r1_diag_slope
        c_diag_slope = np.arange(length)
        return r1_diag_slope, r2_diag_slope, c_diag_slope

    def winning_move(self, player_id: int, nb_in_a_row: int = 4):
        """Check if `player` is winning."""
        r1_diag, r2_diag, c_diag = self.index_diag_slope(nb_in_a_row)
        for c in range(self.nb_cols):
            for r in range(self.nb_rows):
                # Check horizontal locations for win
                if c <= self.nb_cols - nb_in_a_row \
                        and (self.board[r, c: c + nb_in_a_row]
                             == player_id).all():
                    return True

                # Check vertical locations for win
                if r <= self.nb_rows - nb_in_a_row \
                        and (self.board[r: r + nb_in_a_row, c]
                             == player_id).all():
                    return True

                # check diagonals :
                if c <= self.nb_cols - nb_in_a_row \
                        and r <= self.nb_rows - nb_in_a_row:
                    # Check positively sloped diagonals
                    if (self.board[
                            r + r1_diag, c + c_diag] == player_id).all():
                        return True

                    # Check negatively sloped diagonals
                    if (self.board[
                            r + r2_diag, c + c_diag] == player_id).all():
                        return True


class PygameScreen:
    """Manages the pygame display"""

    def __init__(self, width, height):
        self._font = None
        self.screen = self.setup_screen(width, height)

    def setup_font(self, name, size):
        self._font = pygame.font.SysFont(name, size)

    @property
    def font(self) -> pygame.font.Font:
        if self._font is None:
            raise NotSetUpError("Font not defined!"
                                " See `setup_font()` to setup one.")
        return self._font

    @staticmethod
    def setup_screen(width: int, height: int) -> pygame.Surface:
        return pygame.display.set_mode((width, height))

    def prompt_msg(self, msg: str,
                   color, antialias=True, dest=(40, 10)) -> None:
        """Prompts message in color to the screen"""
        label = self.font.render(msg, antialias, color)
        self.screen.blit(label, dest)
        pygame.display.update()


class DisplayManager:
    """Manager of the pygame display"""

    _colors = [BLACK, RED, YELLOW]

    def __init__(self, nb_rows, nb_cols, square_size):
        width = nb_cols * square_size
        height = (nb_rows + 1) * square_size
        self.size = (width, height)
        self.square_size = square_size
        self.nb_rows = nb_rows
        self.nb_cols = nb_cols
        self.radius = square_size // 2 - square_size // 20
        self.screen = PygameScreen(width, height)
        self.grid_color = GRID_COLOR
        self.background_color = BACKGROUND_COLOR

    @staticmethod
    def init_pygame():
        nb_pass, nb_fail = pygame.init()
        print(f"Pygame init done,"
              f" {nb_pass} module(s) passed, {nb_fail} failed.")

    def draw_row_col_square(self, row: int, col: int, color):
        pygame.draw.rect(self.screen.screen, color,
                         (col * self.square_size, row * self.square_size,
                          self.square_size, self.square_size))

    def draw_row_col_circle(self, row: int, col: int, color_id: int):
        pygame.draw.circle(self.screen.screen, self._colors[color_id],
                           (col * self.square_size + self.square_size // 2,
                            row * self.square_size + self.square_size // 2),
                           self.radius)

    def draw_waiting_circle(self, pos_x=None, color_id: int = None):
        pygame.draw.rect(self.screen.screen, self.background_color,
                         (0, 0, self.size[0], self.square_size))
        if pos_x is None or color_id is None:
            return
        pygame.draw.circle(self.screen.screen, self._colors[color_id],
                           (pos_x, self.square_size // 2), RADIUS)
        pygame.display.update()

    def draw_grid(self, board: np.ndarray):
        for r, l_row in enumerate(board):
            for c, id_player in enumerate(l_row):
                self.draw_row_col_square(self.nb_rows-r, c, self.grid_color)
                self.draw_row_col_circle(self.nb_rows-r, c, id_player)
        pygame.display.update()

    def prompt_msg(self, msg: str,
                   color_id, antialias=True, dest=(40, 10)) -> None:
        """Prompts message in color to the screen"""
        self.screen.prompt_msg(msg, self._colors[color_id], antialias, dest)

    def setup_font(self, name: str = "monospace", size: int = 30):
        self.screen.setup_font(name, size)

    def color_from_id(self, id_color: int):
        return self._colors[id_color]


class MainGame:

    def __init__(self, nb_rows, nb_cols, nb_in_a_row,
                 square_size, name_font="monospace", size_font=30):
        # init grid
        self.nb_rows = nb_rows
        self.nb_cols = nb_cols
        self.grid = Grid(nb_rows, nb_cols)

        # init pygame window
        DisplayManager.init_pygame()
        self.display_manager = DisplayManager(nb_rows, nb_cols, square_size)
        self.display_manager.setup_font(name_font, size_font)

        # init game
        self.nb_in_a_row = nb_in_a_row
        self.current_player_id = 1

    def draw_grid(self):
        self.display_manager.draw_grid(self.grid.board)

    def mouse_motion(self, event: pygame.event.Event):
        pos_x = event.pos[0]
        self.display_manager.draw_waiting_circle(pos_x, self.current_player_id)

    def get_col_from_mouse(self, event: pygame.event.Event) -> int:
        pos_x = event.pos[0]
        col = int(math.floor(pos_x / self.display_manager.square_size))
        return col

    def mouse_down(self, event: pygame.event.Event) -> Tuple[bool, bool]:
        col = self.get_col_from_mouse(event)

        if not self.grid.is_valid_location(col):
            return False, False
            # raise InvalidMoveError("Invalid column.")

        self.display_manager.draw_waiting_circle()
        self.grid.drop_piece(col, self.current_player_id)
        # print_board(board)
        self.draw_grid()

        game_over = self.grid.winning_move(self.current_player_id,
                                           self.nb_in_a_row)
        return True, game_over

    def next_player(self):
        self.current_player_id %= NB_PLAYERS
        self.current_player_id += 1

    def win(self):
        self.display_manager.prompt_msg(
            f"Player {self.current_player_id} wins!!", self.current_player_id)


def main():
    game = MainGame(ROW_COUNT, COLUMN_COUNT, NB_IN_A_ROW,
                    SQUARE_SIZE, NAME_FONT, SIZE_FONT)
    game.draw_grid()

    game_over = False
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                game.mouse_motion(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Ask for Player $turn Input
                valid, game_over = game.mouse_down(event)
                if not valid or game_over:
                    break
                game.next_player()

        if game_over:
            game.win()
            pygame.time.wait(3000)


if __name__ == "__main__":
    main()
