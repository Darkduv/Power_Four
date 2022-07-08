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
RADIUS = int(SQUARE_SIZE / 2 - 5)


def init_pygame():
    nb_pass, nb_fail = pygame.init()
    print(f"Pygame init done, {nb_pass} module(s) passed, {nb_fail} failed.")


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board


def drop_piece(board, row, col, piece):
    board[row, col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1, col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r, col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, player_id):
    """Check if `player` is winning"""
    r1_diag_slope = np.arange(NB_IN_A_ROW)
    r2_diag_slope = NB_IN_A_ROW - 1 - r1_diag_slope
    c_diag_slope = np.arange(NB_IN_A_ROW)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            # Check horizontal locations for win
            if c <= COLUMN_COUNT - NB_IN_A_ROW and (board[r, c: c+NB_IN_A_ROW] == player_id).all():
                return True

            # Check vertical locations for win
            if r <= ROW_COUNT - NB_IN_A_ROW and (board[r: r + 4, c] == player_id).all():
                return True

            # check diagonals :
            if c <= COLUMN_COUNT - NB_IN_A_ROW and r <= ROW_COUNT - NB_IN_A_ROW:
                # Check positively sloped diagonals
                if (board[r+r1_diag_slope, c+c_diag_slope] == player_id).all():
                    return True

                # Check negatively sloped diagonals
                if (board[r+r2_diag_slope, c+c_diag_slope] == player_id).all():
                    return True


def draw_board(board, screen, height):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE,
                             (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK, (c * SQUARE_SIZE + SQUARE_SIZE / 2,
                                               r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2),
                               RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            player_ = board[r, c]
            if player_ > 0:
                col_player = COL_PLAYERS[player_]
                pygame.draw.circle(screen, col_player,
                                   (c * SQUARE_SIZE + SQUARE_SIZE // 2,
                                    height - int(r * SQUARE_SIZE + SQUARE_SIZE // 2)), RADIUS)
    pygame.display.update()


def main():
    board = create_board()
    print_board(board)
    game_over = False
    turn = 0

    init_pygame()

    width = COLUMN_COUNT * SQUARE_SIZE
    height = (ROW_COUNT + 1) * SQUARE_SIZE

    size = (width, height)

    screen = pygame.display.set_mode(size)
    draw_board(board, screen, height)
    pygame.display.update()

    myfont = pygame.font.SysFont("monospace", 75)

    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, COL_PLAYERS[turn + 1],
                                   (posx, int(SQUARE_SIZE / 2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                # print(event.pos)
                # Ask for Player 1 Input
                if turn == 0:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARE_SIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 1)

                        if winning_move(board, 1):
                            label = myfont.render("Player 1 wins!!", True, COL_PLAYERS[1])
                            screen.blit(label, (40, 10))
                            game_over = True

                # # Ask for Player 2 Input
                else:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARE_SIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 2)

                        if winning_move(board, 2):
                            label = myfont.render("Player 2 wins!!", True, COL_PLAYERS[2])
                            screen.blit(label, (40, 10))
                            game_over = True

                print_board(board)
                draw_board(board, screen, height)

                turn += 1
                turn = turn % 2

        if game_over:
            pygame.time.wait(3000)


if __name__ == "__main__":
    main()
