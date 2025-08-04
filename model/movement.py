from __future__ import annotations
from typing import Type

from .pieces import Piece, Queen, Rook, Bishop, Knight


class Movement:
    def __init__(
        self,
        origin_square: tuple[int, int],
        target_square: tuple[int, int],
        pawn_promotion: Type[Piece] = Queen,
    ):
        self.origin_square: tuple[int, int] = origin_square
        self.target_square: tuple[int, int] = target_square
        self.pawn_promotion: Type[Piece] = pawn_promotion

    def __str__(self):
        return f"Movement origin={self.origin_square}, target={self.target_square}, promotion={self.pawn_promotion._character}"

    @classmethod
    def create_from_algebraic(cls, notation: str) -> Movement:
        origin_square: tuple[int, int] = Movement.algebraic_to_square(notation[0:2])
        target_square: tuple[int, int] = Movement.algebraic_to_square(notation[2:4])

        # if pawn promotion specified
        if len(notation) == 5:
            match notation[4]:
                case "q":
                    promotion: Type[Piece] = Queen
                case "r":
                    promotion: Type[Piece] = Rook
                case "b":
                    promotion: Type[Piece] = Bishop
                case "n":
                    promotion: Type[Piece] = Knight
                case _:
                    promotion: Type[Piece] = Queen

            return cls(origin_square, target_square, promotion)

        else:
            return cls(origin_square, target_square)

    @staticmethod
    def algebraic_to_square(coordinate_pair: str) -> tuple[int, int]:
        """
        Converts algebraic coordinate pair to square tuple
        e.g. "e6" -> tuple(4, 2)
        """
        column: int = ord(coordinate_pair[0]) - 97  # 97 is code for 'a'
        row: int = 8 - int(coordinate_pair[1])

        return (column, row)
