"""
Credits: code found online
"""

import numpy as np
import pygame
import sys
import math

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

NB_IN_A_ROW = 4

COL_PLAYERS = [BLACK, RED, YELLOW]

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

    def setup_font(self, name: str = "monospace", size: int = 30):
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
                   color, antialias=True, label=None, dest=(40, 10)) -> None:
        """Prompts message in color to the screen"""
        if label is None:
            label = self.font.render(msg, antialias, color)
        self.screen.blit(label, dest)
        pygame.display.update()


class DisplayManager:
    """Manager of the pygame display"""

    def __init__(self, nb_rows, nb_cols, square_size):
        width = nb_cols * square_size
        height = (nb_rows + 1) * square_size
        self.size = (width, height)
        self.square_size = square_size
        self.radius = square_size // 2 - square_size // 20
        self.screen = PygameScreen(width, height)

    @staticmethod
    def init_pygame():
        nb_pass, nb_fail = pygame.init()
        print(f"Pygame init done,"
              f" {nb_pass} module(s) passed, {nb_fail} failed.")


def draw_board(board: np.ndarray, screen):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE,
                             (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE,
                              SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(
                screen, BLACK,
                (c * SQUARE_SIZE + SQUARE_SIZE / 2,
                 (r + 1) * SQUARE_SIZE + SQUARE_SIZE / 2), RADIUS)
            player_ = board[ROW_COUNT-1-r, c]
            if player_ > 0:
                col_player = COL_PLAYERS[player_]
                pygame.draw.circle(
                    screen, col_player,
                    (c * SQUARE_SIZE + SQUARE_SIZE // 2,
                     (r + 1) * SQUARE_SIZE + SQUARE_SIZE // 2), RADIUS)
    pygame.display.update()


def main():
    grid = Grid(ROW_COUNT, COLUMN_COUNT)
    # print_board(board)
    current_player_id = 1

    DisplayManager.init_pygame()

    width = COLUMN_COUNT * SQUARE_SIZE

    pygame_manager = DisplayManager(ROW_COUNT, COLUMN_COUNT, SQUARE_SIZE)
    window = pygame_manager.screen
    window.setup_font(NAME_FONT, SIZE_FONT)

    draw_board(grid.board, window.screen)

    game_over = False
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(window.screen, BLACK,
                                 (0, 0, width, SQUARE_SIZE))
                posx = event.pos[0]
                pygame.draw.circle(window.screen,
                                   COL_PLAYERS[current_player_id],
                                   (posx, int(SQUARE_SIZE / 2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(window.screen, BLACK,
                                 (0, 0, width, SQUARE_SIZE))
                # print(event.pos)
                # Ask for Player $turn Input

                posx = event.pos[0]
                col = int(math.floor(posx / SQUARE_SIZE))

                if not grid.is_valid_location(col):
                    break

                grid.drop_piece(col, current_player_id)
                # print_board(board)
                draw_board(grid.board, window.screen)

                if grid.winning_move(current_player_id, NB_IN_A_ROW):
                    window.prompt_msg(f"Player {current_player_id} wins!!",
                                      COL_PLAYERS[current_player_id])
                    game_over = True

                current_player_id %= NB_PLAYERS
                current_player_id += 1

        if game_over:
            pygame.time.wait(3000)


if __name__ == "__main__":
    main()
