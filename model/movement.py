from __future__ import annotations
from typing import override

from .pieces import Piece, Queen, Rook, Bishop, Knight


class Movement:
    def __init__(
        self,
        origin_square: tuple[int, int],
        target_square: tuple[int, int],
        pawn_promotion: type[Piece] = Queen,
    ):
        self.origin_square: tuple[int, int] = origin_square
        self.target_square: tuple[int, int] = target_square
        self.pawn_promotion: type[Piece] = pawn_promotion

    @override
    def __str__(self):
        return f"Movement origin={self.origin_square}, target={self.target_square}"

    @classmethod
    def create_from_algebraic(cls, notation: str) -> Movement:
        origin_square: tuple[int, int] = Movement.algebraic_to_square(notation[0:2])
        target_square: tuple[int, int] = Movement.algebraic_to_square(notation[2:4])

        # if pawn promotion specified
        if len(notation) == 5:
            promotion: type[Piece] = Queen
            match notation[4]:
                case "r":
                    promotion = Rook
                case "b":
                    promotion = Bishop
                case "n":
                    promotion = Knight
                case _:
                    raise Exception(f"Unknown promotion character '{notation[4]}'")

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
