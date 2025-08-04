from __future__ import annotations # lazy loads type annotations

class Piece:
    name = "Piece"
    nerdfont_character = " "
    _character = " "

    board_width = 8
    board_height = 8

    def __init__(self, is_white: bool):
        self.is_white = is_white
        self.has_moved = False

    def __str__(self) -> str:
        return f"{self.name} (white={self.is_white}, moved={self.has_moved})"

    def get_moveable_squares(self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]) -> set[tuple[int, int]]:
        raise NotImplementedError("Cannot get moveable squares from abstract Piece class.")

    def get_ascii_character(self) -> str:
        return self._character.upper() if self.is_white else self._character

    def _in_bounds(self, square: tuple[int, int]) -> bool:
        if square[0] < 0 or square[0] >= self.board_width:
            return False
        elif square[1] < 0 or square[1] >= self.board_height:
            return False
        else:
            return True


class Pawn(Piece):
    name = "Pawn"
    nerdfont_character = "󰡙"
    _character = "p"

    def get_moveable_squares(self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]) -> set[tuple[int, int]]:
        direction: int = -1 if self.is_white else 1
        moveable_squares: set[tuple[int, int]] = set()

        # move forward by one square
        new_square: tuple[int, int] = (square[0], square[1] + direction)
        if self._in_bounds(new_square) and new_square not in pieces:
            moveable_squares.add(new_square)

        # move forward by two squares from starting position
        if not self.has_moved:
            new_square = (square[0], square[1] + 2 * direction)
            in_between_square = (square[0], square[1] + direction)
            if self._in_bounds(new_square):
                if new_square not in pieces and in_between_square not in pieces:
                    moveable_squares.add(new_square)

        # capture diagonally
        for modifier in [(-1, direction), (1, direction)]:
            new_square = (square[0] + modifier[0], square[1] + modifier[1])
            if new_square in pieces and pieces[new_square].is_white != self.is_white:
                moveable_squares.add(new_square)

        return moveable_squares


class Knight(Piece):
    name = "Knight"
    nerdfont_character = "󰡘"
    _character = "n"

    def get_moveable_squares(self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]) -> set[tuple[int, int]]:
        moveable_squares: set[tuple[int, int]] = set()
        modifiers: list[tuple[int, int]] = [(-1, -2), (1, -2), (2, -1), (2, 1), (-1, 2), (1, 2), (-2, -1), (-2, 1)]

        for modifier in modifiers:
            new_square: tuple[int, int] = (square[0] + modifier[0], square[1] + modifier[1])
            if self._in_bounds(new_square):
                if new_square not in pieces:
                    moveable_squares.add(new_square)
                elif pieces[new_square].is_white != self.is_white:
                    moveable_squares.add(new_square)

        return moveable_squares


class Bishop(Piece):
    name = "Bishop"
    nerdfont_character = "󰡜"
    _character = "b"

    def get_moveable_squares(self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]) -> set[tuple[int, int]]:
        moveable_squares: set[tuple[int, int]] = set()
        directions: list[tuple[int, int]] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for direction in directions:
            increment: int = 1
            while True:
                new_square: tuple[int, int] = (square[0] + direction[0] * increment, square[1] + direction[1] * increment)
                if self._in_bounds(new_square):
                    if new_square not in pieces:
                        moveable_squares.add(new_square)
                        increment += 1
                    else:
                        if pieces[new_square].is_white != self.is_white:
                            moveable_squares.add(new_square)
                        break
                else:
                    break

        return moveable_squares


class Rook(Piece):
    name = "Rook"
    nerdfont_character = "󰡛"
    _character = "r"

    def get_moveable_squares(self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]) -> set[tuple[int, int]]:
        moveable_squares: set[tuple[int, int]] = set()
        directions: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for direction in directions:
            increment: int = 1
            while True:
                new_square: tuple[int, int] = (square[0] + direction[0] * increment, square[1] + direction[1] * increment)
                if self._in_bounds(new_square):
                    if new_square not in pieces:
                        moveable_squares.add(new_square)
                        increment += 1
                    else:
                        if pieces[new_square].is_white != self.is_white:
                            moveable_squares.add(new_square)
                        break
                else:
                    break

        return moveable_squares


class Queen(Piece):
    name = "Queen"
    nerdfont_character = "󰡚"
    _character = "q"

    def get_moveable_squares(self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]) -> set[tuple[int, int]]:
        moveable_squares: set[tuple[int, int]] = set()
        moveable_squares = moveable_squares.union(Bishop.get_moveable_squares(Bishop(self.is_white), pieces, square))
        moveable_squares = moveable_squares.union(Rook.get_moveable_squares(Rook(self.is_white), pieces, square))
        return moveable_squares

class King(Piece):
    name = "King"
    nerdfont_character = "󰡗"
    _character = "k"

    def get_moveable_squares(self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]) -> set[tuple[int, int]]:
        moveable_squares: set[tuple[int, int]] = set()
        modifiers: list[tuple[int, int]] = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for modifier in modifiers:
            new_square: tuple[int, int] = (square[0] + modifier[0], square[1] + modifier[1])
            if self._in_bounds(new_square):
                if new_square not in pieces:
                    moveable_squares.add(new_square)
                elif pieces[new_square].is_white != self.is_white:
                    moveable_squares.add(new_square)

        return moveable_squares
