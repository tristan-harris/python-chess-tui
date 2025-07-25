import curses
from enum import Enum

from board import Board
from pieces import Piece

WINDOW_WIDTH = 16
WINDOW_HEIGHT = 16
WINDOW_LEFT_PADDING = 1
WINDOW_TOP_PADDING = 1


class Color(Enum):
    BLACK = 0
    WHITE = 15
    BLUE = 20
    GREEN = 28
    BROWN = 94
    GRAY = 246


def main(stdscr: curses.window):
    curses.start_color()
    curses.use_default_colors()

    if curses.COLORS < 256:
        stdscr.addstr(0, 0, "Your terminal does not support 256 colors.")
        stdscr.addstr(1, 0, "Press any key to quit...")
        stdscr.getch()
        return

    curses.curs_set(0)  # hide cursor
    stdscr.clear()

    board = Board()
    board.setup_pieces()

    draw_board(stdscr, board)

    stdscr.getch()


def draw_board(stdscr: curses.window, board: Board):
    for y in range(board.height):
        for x in range(board.width):
            background_color = (
                Color.GREEN.value if (x + y) % 2 == 0 else Color.GRAY.value
            )
            foreground_color = background_color
            piece_character = " "

            if (x, y) in board.pieces:
                foreground_color = (
                    Color.WHITE.value
                    if board.pieces[(x, y)].white
                    else Color.BLACK.value
                )
                piece_character = board.pieces[(x, y)].character


            curses.init_pair(1, foreground_color, background_color)
            stdscr.addstr(
                y, x * 3, f" {piece_character} ", curses.color_pair(1)
            )


if __name__ == "__main__":
    curses.wrapper(main)
