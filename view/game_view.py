from __future__ import annotations # lazy loads type annotations

from blessed import Terminal
from blessed.keyboard import Keystroke

from util import log

from .cursor import Cursor
from model.board import Board
from model.pieces import Piece

class GameView:
    def __init__(self, board: Board):
        self.term: Terminal = Terminal()
        self.selection_cursor: Cursor = Cursor(self.term.on_teal, board.width, board.height, square=(4, 6)) # choosing a piece
        self.movement_cursor: Cursor = Cursor(self.term.on_aqua, board.width, board.height) # moving a piece
        self.board: Board = board
        self.state = SelectingState(self)

    def change_state(self, new_state: GameViewState):
        if isinstance(self.state, GameViewState):
            self.state.exit()
        self.state = new_state
        self.state.enter()

    def set_board(self, new_board: Board):
        self.board = new_board

    def run(self):
        with self.term.hidden_cursor(), self.term.cbreak():
            self.draw_board()

            while True:
                user_input: Keystroke = self.term.inkey()
                if user_input == "q":
                    print(self.term.home + self.term.clear)  # clear screen
                    break
                else:
                    self.state.handle_input(user_input)

    def move_cursor(self, cursor: tuple, x_diff: int, y_diff: int):
        new_x: int = cursor[0] + x_diff
        new_y: int = cursor[1] + y_diff
        if 0 <= new_x < self.board.width and 0 <= new_y < self.board.height:
            cursor = (new_x, new_y)
            self.draw_board()

    def draw_board(self, moveable_squares: set[tuple[int, int]] = set()):
        print(self.term.home + self.term.clear)  # clear screen

        for y in range(self.board.height):
            for x in range(self.board.width):

                if self.movement_cursor.square == (x, y) and isinstance(self.state, MovingState):
                    background_color = self.movement_cursor.color
                elif self.selection_cursor.square == (x, y):
                    if isinstance(self.state, MovingState):
                        background_color = self.selection_cursor.color
                    else:
                        background_color = self.selection_cursor.color
                elif (x, y) in moveable_squares:
                    background_color = self.term.on_lightblue4
                elif (x + y) % 2 == 0:
                    background_color = self.term.on_navajowhite4
                else:
                    background_color = self.term.on_gray40

                if (x, y) in self.board.get_pieces():
                    if self.board.get_pieces()[(x, y)].white:
                        foreground_color = self.term.gray100
                    else:
                        foreground_color = self.term.gray0
                    character = self.board.get_pieces()[(x, y)].nf_character
                else:
                    foreground_color = background_color
                    character = " "

                self.term.move_xy(x * 3, y)
                print(f"{foreground_color}{background_color} {character} {self.term.normal}", end="")

            print() # next row

        print("text")

    def select_square(self, square: tuple[int, int]):
        if square in self.board.get_pieces():
            self.change_state(MovingState(self, self.board.get_moveable_squares(square)))

    def move_piece(self, piece_square: tuple[int, int], target_square: tuple[int, int], moveable_squares: set[tuple[int, int]]):
        if piece_square in self.board.get_pieces():
            if self.movement_cursor.square in moveable_squares:
                self.board.move_piece(piece_square, target_square)
                self.selection_cursor.square = target_square
                self.change_state(SelectingState(self))


class GameViewState:
    def __init__(self, view: GameView):
        self.view = view

    def enter(self):
        pass

    def handle_input(self, user_input: Keystroke):
        pass

    def exit(self):
        pass


class SelectingState(GameViewState):
    def enter(self):
        self.view.draw_board()

    def handle_input(self, user_input: Keystroke):
        super().handle_input(user_input)

        redraw = True

        if user_input.is_sequence:
            match (user_input.name):
                case "KEY_LEFT":
                    self.view.selection_cursor.move(-1, 0)
                case "KEY_DOWN":
                    self.view.selection_cursor.move(0, 1)
                case "KEY_RIGHT":
                    self.view.selection_cursor.move(1, 0)
                case "KEY_UP":
                    self.view.selection_cursor.move(0, -1)
                case _:
                    redraw = False
        else:
            match (user_input.lower()):
                case "h":
                    self.view.selection_cursor.move(-1, 0)
                case "j":
                    self.view.selection_cursor.move(0, 1)
                case "k":
                    self.view.selection_cursor.move(0, -1)
                case "l":
                    self.view.selection_cursor.move(1, 0)
                case " ":
                    self.view.select_square(self.view.selection_cursor.square)
                    redraw = False
                case _:
                    redraw = False

        if redraw:
            self.view.draw_board()


class MovingState(GameViewState):
    def __init__(self, view: GameView, moveable_squares: set[tuple[int, int]]):
        super().__init__(view)
        self.moveable_squares: set[tuple[int, int]] = moveable_squares

    def enter(self):
        self.view.movement_cursor.square = self.view.selection_cursor.square
        self.view.draw_board(moveable_squares=self.moveable_squares)

    def handle_input(self, user_input):
        super().handle_input(user_input)

        redraw = True

        if user_input.is_sequence:
            match (user_input.name):
                case "KEY_ESCAPE":
                    self.view.change_state(SelectingState(self.view))
                    redraw = False
                case "KEY_LEFT":
                    self.view.movement_cursor.move(-1, 0)
                case "KEY_DOWN":
                    self.view.movement_cursor.move(0, 1)
                case "KEY_RIGHT":
                    self.view.movement_cursor.move(1, 0)
                case "KEY_UP":
                    self.view.movement_cursor.move(0, -1)
                case _:
                    redraw = False

        else:
            match (user_input.lower()):
                case "h":
                    self.view.movement_cursor.move(-1, 0)
                case "j":
                    self.view.movement_cursor.move(0, 1)
                case "k":
                    self.view.movement_cursor.move(0, -1)
                case "l":
                    self.view.movement_cursor.move(1, 0)
                case " ":
                    self.view.move_piece(self.view.selection_cursor.square, self.view.movement_cursor.square, self.moveable_squares)
                    redraw = False
                case _:
                    redraw = False

        if redraw:
            self.view.draw_board(moveable_squares=self.moveable_squares)


class NoInputState(GameViewState):
    pass
