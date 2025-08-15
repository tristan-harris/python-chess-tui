from __future__ import annotations
from typing import override


class Piece:
    name: str = "Piece"
    nerdfont_character: str = " "
    _character: str = " "

    board_width: int = 8
    board_height: int = 8

    def __init__(self, is_white: bool):
        self.is_white: bool = is_white
        self.has_moved: bool = False

    @override
    def __str__(self) -> str:
        return f"{self.name} (white={self.is_white}, moved={self.has_moved})"

    @property
    def character(self) -> str:
        return self._character.upper() if self.is_white else self._character

    def get_moveable_squares(
        self, _pieces: dict[tuple[int, int], Piece], _square: tuple[int, int]
    ) -> set[tuple[int, int]]:
        raise NotImplementedError("Cannot get moveable squares from abstract Piece class.")

    def _get_moveable_squares_by_directions(
        self,
        pieces: dict[tuple[int, int], Piece],
        square: tuple[int, int],
        directions: list[tuple[int, int]],
        repeat: bool,
    ) -> set[tuple[int, int]]:
        """
        Helper method for every piece except Pawn.
        If repeat=True, keep searching in every direction.
        """
        moveable_squares: set[tuple[int, int]] = set()

        for direction in directions:
            increment: int = 1
            while True:
                new_square: tuple[int, int] = (
                    square[0] + direction[0] * increment,
                    square[1] + direction[1] * increment,
                )
                if self._in_bounds(new_square):
                    if new_square not in pieces:
                        moveable_squares.add(new_square)
                        if repeat:
                            increment += 1
                        else:
                            break
                    else:
                        if pieces[new_square].is_white != self.is_white:
                            moveable_squares.add(new_square)
                        break
                else:
                    break

        return moveable_squares

    def _in_bounds(self, square: tuple[int, int]) -> bool:
        if square[0] < 0 or square[0] >= self.board_width:
            return False
        elif square[1] < 0 or square[1] >= self.board_height:
            return False
        else:
            return True


class Pawn(Piece):
    name: str = "Pawn"
    nerdfont_character: str = "󰡙"
    _character: str = "p"

    @override
    def get_moveable_squares(
        self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]
    ) -> set[tuple[int, int]]:
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
    name: str = "Knight"
    nerdfont_character: str = "󰡘"
    _character: str = "n"

    @override
    def get_moveable_squares(
        self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]
    ) -> set[tuple[int, int]]:
        directions: list[tuple[int, int]] = [
            (-1, -2),
            (1, -2),
            (2, -1),
            (2, 1),
            (-1, 2),
            (1, 2),
            (-2, -1),
            (-2, 1),
        ]
        return self._get_moveable_squares_by_directions(pieces, square, directions, repeat=False)


class Bishop(Piece):
    name: str = "Bishop"
    nerdfont_character: str = "󰡜"
    _character: str = "b"

    @override
    def get_moveable_squares(
        self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]
    ) -> set[tuple[int, int]]:
        directions: list[tuple[int, int]] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._get_moveable_squares_by_directions(pieces, square, directions, repeat=True)


class Rook(Piece):
    name: str = "Rook"
    nerdfont_character: str = "󰡛"
    _character: str = "r"

    @override
    def get_moveable_squares(
        self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]
    ) -> set[tuple[int, int]]:
        directions: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self._get_moveable_squares_by_directions(pieces, square, directions, repeat=True)


class Queen(Piece):
    name: str = "Queen"
    nerdfont_character: str = "󰡚"
    _character: str = "q"

    @override
    def get_moveable_squares(
        self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]
    ) -> set[tuple[int, int]]:
        directions: list[tuple[int, int]] = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        return self._get_moveable_squares_by_directions(pieces, square, directions, repeat=True)


class King(Piece):
    name: str = "King"
    nerdfont_character: str = "󰡗"
    _character: str = "k"

    @override
    def get_moveable_squares(
        self, pieces: dict[tuple[int, int], Piece], square: tuple[int, int]
    ) -> set[tuple[int, int]]:
        directions: list[tuple[int, int]] = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        return self._get_moveable_squares_by_directions(pieces, square, directions, repeat=False)
