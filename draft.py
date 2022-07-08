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
SIZE_FONT = 75
NAME_FONT = "monospace"
RADIUS = SQUARE_SIZE // 2 - 5

NB_PLAYERS = 2


class InvalidMoveError(Exception):
    """Custom error for invalid moves."""


def init_pygame():
    nb_pass, nb_fail = pygame.init()
    print(f"Pygame init done, {nb_pass} module(s) passed, {nb_fail} failed.")


def setup_font(name: str = NAME_FONT, size: int = SIZE_FONT)\
        -> pygame.font.Font:
    return pygame.font.SysFont(name, size)


def setup_screen(width: int, height: int) -> pygame.Surface:
    return pygame.display.set_mode((width, height))


def create_board() -> np.ndarray:
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board


def drop_piece(board: np.ndarray, col: int, id_player: int):
    """Drop the piece in the column."""
    row = get_next_open_row(board, col)
    board[row, col] = id_player


def is_valid_location(board: np.ndarray, col: int) -> bool:
    """Checks if a column is a valid location for a piece."""
    return board[ROW_COUNT - 1, col] == 0


def get_next_open_row(board: np.ndarray, col: int) -> int:
    """Finds the first row where a new piece can go.

    This row must be a valid location"""
    for r in range(ROW_COUNT):
        if board[r, col] == 0:
            return r
    raise InvalidMoveError("This column is filled. Please try another.")


def print_board(board: np.ndarray):
    print(np.flip(board, 0))


def winning_move(board: np.ndarray, player_id: int):
    """Check if `player` is winning."""
    r1_diag_slope = np.arange(NB_IN_A_ROW)
    r2_diag_slope = NB_IN_A_ROW - 1 - r1_diag_slope
    c_diag_slope = np.arange(NB_IN_A_ROW)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            # Check horizontal locations for win
            if c <= COLUMN_COUNT - NB_IN_A_ROW \
                    and (board[r, c: c+NB_IN_A_ROW] == player_id).all():
                return True

            # Check vertical locations for win
            if r <= ROW_COUNT - NB_IN_A_ROW \
                    and (board[r: r + NB_IN_A_ROW, c] == player_id).all():
                return True

            # check diagonals :
            if c <= COLUMN_COUNT - NB_IN_A_ROW and r <= ROW_COUNT - NB_IN_A_ROW:
                # Check positively sloped diagonals
                if (board[r+r1_diag_slope, c+c_diag_slope] == player_id).all():
                    return True

                # Check negatively sloped diagonals
                if (board[r+r2_diag_slope, c+c_diag_slope] == player_id).all():
                    return True


def draw_board(board: np.ndarray, screen):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE,
                             (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE,
                              SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(
                screen, BLACK,
                (c * SQUARE_SIZE + SQUARE_SIZE / 2,
                 r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            player_ = board[r, c]
            if player_ > 0:
                col_player = COL_PLAYERS[player_]
                pygame.draw.circle(
                    screen, col_player,
                    (c * SQUARE_SIZE + SQUARE_SIZE // 2,
                     (ROW_COUNT - r) * SQUARE_SIZE + SQUARE_SIZE // 2), RADIUS)
    pygame.display.update()


def main():
    board = create_board()
    print_board(board)
    turn = 1

    init_pygame()
    my_font = setup_font()

    width = COLUMN_COUNT * SQUARE_SIZE
    height = (ROW_COUNT + 1) * SQUARE_SIZE

    screen = setup_screen(width, height)
    draw_board(board, screen)
    pygame.display.update()

    game_over = False
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, COL_PLAYERS[turn],
                                   (posx, int(SQUARE_SIZE / 2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                # print(event.pos)
                # Ask for Player $turn Input

                posx = event.pos[0]
                col = int(math.floor(posx / SQUARE_SIZE))

                if not is_valid_location(board, col):
                    break

                drop_piece(board, col, turn)

                if winning_move(board, turn):
                    label = my_font.render(f"Player {turn} wins!!",
                                           True, COL_PLAYERS[turn])
                    screen.blit(label, (40, 10))
                    game_over = True

                print_board(board)
                draw_board(board, screen)

                turn %= NB_PLAYERS
                turn += 1

        if game_over:
            pygame.time.wait(3000)


if __name__ == "__main__":
    main()
