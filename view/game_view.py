from __future__ import annotations  # lazy loads type annotations
import asyncio
from typing import Callable

from blessed import Terminal
from blessed.keyboard import Keystroke

from .cursor import Cursor
from controller.exceptions import EndGameException
from controller.game_config import GameConfig
from model.board import Board
from model.movement import Movement
from model.pieces import Piece

PADDING: int = 2


class GameView:
    def __init__(self, board: Board, send_movement: Callable[[Movement]], game_config: GameConfig):
        self.term: Terminal = Terminal()
        self.game_config: GameConfig = game_config

        self.colors: dict[str, str] = {
            "white_square_background": self.term.on_seashell4,
            "black_square_background": self.term.on_gray40,
            "cursor_background": self.term.on_cyan3,
            "selected_square_background": self.term.on_darkslategray4,
            "moveable_square_background": self.term.on_lightblue4,
            "white_piece_foreground": self.term.gray100,
            "black_piece_foreground": self.term.gray0,
        }

        # used to choose a piece
        self.selection_cursor: Cursor = Cursor(0, 0, board.width - 1, board.height - 1)

        # used to choose a square to move to
        self.movement_cursor: Cursor = Cursor(0, 0, board.width - 1, board.height - 1)

        self.board: Board = board
        self.send_movement: Callable[[Movement]] = send_movement

        self.is_ready: bool = False
        self.state: GameViewState = NoInputState(self)

    async def set_board(self, new_board: Board):
        self.board = new_board
        await self.state.draw_board()

    async def enable_input(self):
        await self._change_state(SelectingState(self))

    async def disable_input(self):
        await self._change_state(NoInputState(self))

    async def run(self):
        try:
            with self.term.hidden_cursor(), self.term.cbreak():
                print(self.term.home + self.term.clear)
                await self.state.draw_board()
                self.is_ready = True

                while True:
                    user_input: Keystroke = self.term.inkey(timeout=0.01)
                    if user_input == "q":
                        print(self.term.home + self.term.clear)
                        raise EndGameException()
                    else:
                        await self.state.handle_input(user_input)

                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            print(self.term.home + self.term.clear)
            raise

    async def draw_board(self, draw_cursors: bool, moveable_squares: set[tuple[int, int]] = set()):
        print(self.term.home)

        pieces: dict[tuple[int, int], Piece] = self.board.get_pieces()

        for y in range(self.board.height):
            print(" " * PADDING, end="")
            for x in range(self.board.width):
                background_color: str = ""

                if draw_cursors:
                    if isinstance(self.state, SelectingState):
                        if self.selection_cursor.square == (x, y):
                            background_color = self.colors["cursor_background"]
                    elif isinstance(self.state, MovingState):
                        if self.movement_cursor.square == (x, y):
                            background_color = self.colors["cursor_background"]
                        elif self.selection_cursor.square == (x, y):
                            background_color = self.colors["selected_square_background"]
                        elif (x, y) in moveable_squares:
                            background_color = self.colors["moveable_square_background"]

                if background_color == "":
                    if (x + y) % 2 == 0:
                        background_color = self.colors["white_square_background"]
                    else:
                        background_color = self.colors["black_square_background"]

                foreground_color: str = background_color
                piece_character: str = " "

                if (x, y) in pieces:
                    piece: Piece = pieces[(x, y)]

                    if piece.is_white:
                        foreground_color = self.colors["white_piece_foreground"]
                    else:
                        foreground_color = self.colors["black_piece_foreground"]

                    if self.game_config.ascii:
                        piece_character = piece.get_ascii_character()
                    else:
                        piece_character = piece.nerdfont_character

                self.term.move_xy(x * 3, y)

                print(
                    f"{foreground_color}{background_color} {piece_character} {self.term.normal}",
                    end="",
                )

            # divider
            print(" ┃ ", end="")

            # white player status
            if y == 0:
                text: str = f"White: {self.get_player_name(white=True)}"
                if self.board.white_turn:
                    text = f"{self.term.bold}{text}{self.term.normal}"
                print(text, end="")

            # black player status
            elif y == 1:
                text: str = f"Black: {self.get_player_name(white=False)}"
                if not self.board.white_turn:
                    text = f"{self.term.bold}{text}{self.term.normal}"
                print(text, end="")

            print()  # move down to next row

        # pad check status to fully clear previous line
        print(f"{self.get_check_status(self.board):<22}")

    def get_player_name(self, white: bool) -> str:
        """Returns name of engine (based on filename) or 'Human' if no engine"""
        engine_path: str | None = (
            self.game_config.white_engine_path if white else self.game_config.black_engine_path
        )
        if engine_path:
            return engine_path.rsplit("/")[-1]
        else:
            return "Human"

    def get_check_status(self, board: Board) -> str:
        if board.game_over:
            if board.is_king_in_checkmate(board.white_turn):
                if board.white_turn:
                    return "Checkmate. Black wins!"
                else:
                    return "Checkmate. White wins!"
            else:
                return "Draw."
        else:
            if board.is_king_in_check(board.white_turn):
                if board.white_turn:
                    return "White is in check."
                else:
                    return "Black is in check."
            else:
                return ""

    async def select_square(self, square: tuple[int, int]):
        if square in self.board.get_pieces():
            if self.board.get_pieces()[square].is_white == self.board.white_turn:
                await self._change_state(MovingState(self, self.board.get_moveable_squares(square)))

    async def move_piece(
        self,
        piece_square: tuple[int, int],
        target_square: tuple[int, int],
        moveable_squares: set[tuple[int, int]],
    ):
        if piece_square in self.board.get_pieces():
            if self.movement_cursor.square in moveable_squares:
                self.selection_cursor.square = target_square
                await self._change_state(SelectingState(self))

                movement: Movement = Movement(piece_square, target_square)
                await self.send_movement(movement)

    async def _change_state(self, new_state: GameViewState):
        if self.state.__class__ != new_state.__class__:
            await self.state.exit()
            self.state = new_state
            await self.state.enter()


class GameViewState:
    def __init__(self, view: GameView):
        self.view = view

    async def enter(self):
        pass

    async def handle_input(self, user_input: Keystroke):
        pass

    async def draw_board(self):
        pass

    async def exit(self):
        pass


class SelectingState(GameViewState):
    async def enter(self):
        await self.draw_board()

    async def handle_input(self, user_input: Keystroke):
        redraw: bool = True
        state_cursor: Cursor = self.view.selection_cursor

        if user_input.is_sequence:
            match user_input.name:
                case "KEY_LEFT":
                    state_cursor.move(-1, 0)
                case "KEY_DOWN":
                    state_cursor.move(0, 1)
                case "KEY_RIGHT":
                    state_cursor.move(1, 0)
                case "KEY_UP":
                    state_cursor.move(0, -1)
                case _:
                    redraw = False
        else:
            match user_input.lower():
                case "h":
                    state_cursor.move(-1, 0)
                case "j":
                    state_cursor.move(0, 1)
                case "l":
                    state_cursor.move(1, 0)
                case "k":
                    state_cursor.move(0, -1)
                case " ":
                    await self.view.select_square(state_cursor.square)
                    redraw = False
                case _:
                    redraw = False

        if redraw:
            await self.draw_board()

    async def draw_board(self):
        await self.view.draw_board(draw_cursors=True)


class MovingState(GameViewState):
    def __init__(self, view: GameView, moveable_squares: set[tuple[int, int]]):
        super().__init__(view)
        self.moveable_squares: set[tuple[int, int]] = moveable_squares

    async def enter(self):
        self.view.movement_cursor.square = self.view.selection_cursor.square
        await self.draw_board()

    async def handle_input(self, user_input: Keystroke):
        redraw: bool = True
        state_cursor: Cursor = self.view.movement_cursor

        if user_input.is_sequence:
            match user_input.name:
                case "KEY_ESCAPE":
                    await self.view._change_state(SelectingState(self.view))
                    redraw = False
                case "KEY_LEFT":
                    state_cursor.move(-1, 0)
                case "KEY_DOWN":
                    state_cursor.move(0, 1)
                case "KEY_RIGHT":
                    state_cursor.move(1, 0)
                case "KEY_UP":
                    state_cursor.move(0, -1)
                case _:
                    redraw = False

        else:
            match user_input.lower():
                case "h":
                    state_cursor.move(-1, 0)
                case "j":
                    state_cursor.move(0, 1)
                case "l":
                    state_cursor.move(1, 0)
                case "k":
                    state_cursor.move(0, -1)
                case " ":
                    await self.view.move_piece(
                        self.view.selection_cursor.square,
                        state_cursor.square,
                        self.moveable_squares,
                    )
                    redraw = False  # draw handle by state transition
                case _:
                    redraw = False

        if redraw:
            await self.draw_board()

    async def draw_board(self):
        await self.view.draw_board(draw_cursors=True, moveable_squares=self.moveable_squares)


class NoInputState(GameViewState):
    async def enter(self):
        await self.draw_board()

    async def draw_board(self):
        await self.view.draw_board(draw_cursors=False)
