from __future__ import annotations  # lazy loads type annotations
import copy
from typing import Type

from .movement import Movement
from .pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class Board:
    width = 8
    height = 8

    def __init__(self):
        self._pieces: dict[tuple[int, int], Piece] = {}
        self.white_turn: bool = True
        self.game_over: bool = False

        # keeps track of pawn two square movements for en passant
        # set to new position of moved pawn
        # set again or reset at the end of next turn
        self.pawn_double_move: tuple[int, int] | None = None

        self.halfmove_clock = 0
        self.fullmove_number = 1

    def setup_pieces(self):
        """Setups chess board with standard configuration"""
        self._pieces = {}

        # rows of pawns for both sides
        for x in range(self.width):
            self._pieces[(x, 6)] = Pawn(True)
            self._pieces[(x, 1)] = Pawn(False)

        # white
        self._pieces[(0, 7)] = Rook(True)
        self._pieces[(1, 7)] = Knight(True)
        self._pieces[(2, 7)] = Bishop(True)
        self._pieces[(3, 7)] = Queen(True)
        self._pieces[(4, 7)] = King(True)
        self._pieces[(5, 7)] = Bishop(True)
        self._pieces[(6, 7)] = Knight(True)
        self._pieces[(7, 7)] = Rook(True)

        # black
        self._pieces[(0, 0)] = Rook(False)
        self._pieces[(1, 0)] = Knight(False)
        self._pieces[(2, 0)] = Bishop(False)
        self._pieces[(3, 0)] = Queen(False)
        self._pieces[(4, 0)] = King(False)
        self._pieces[(5, 0)] = Bishop(False)
        self._pieces[(6, 0)] = Knight(False)
        self._pieces[(7, 0)] = Rook(False)


    def get_moveable_squares(self, square: tuple[int, int]) -> set[tuple[int, int]]:
        if square not in self._pieces:
            raise Exception(f"No piece found at {square}")

        valid_squares: set[tuple[int, int]] = set()
        moveable_squares = self._pieces[square].get_moveable_squares(self._pieces, square)

        moveable_squares = moveable_squares.union(self.get_en_passant_movement(square))
        moveable_squares = moveable_squares.union(self.get_castling_movements(square))

        for moveable_square in moveable_squares:
            movement: Movement = Movement(square, moveable_square)
            new_board: Board = self.move_piece(movement)
            if not new_board.is_king_in_check(new_board._pieces[moveable_square].is_white):
                valid_squares.add(moveable_square)

        return valid_squares

    def get_en_passant_movement(self, square: tuple[int, int]) -> set[tuple[int, int]]:
        movements: set[tuple[int, int]] = set()
        if isinstance(self._pieces[square], Pawn):
            if self.pawn_double_move != None:
                if abs(self.pawn_double_move[0] - square[0]) == 1:
                    if self.pawn_double_move[1] == square[1]:
                        direction = 1 if self._pieces[self.pawn_double_move].is_white else -1
                        movements.add(
                            (self.pawn_double_move[0], self.pawn_double_move[1] + direction)
                        )
        return movements

    def get_castling_movements(self, square: tuple[int, int]) -> set[tuple[int, int]]:
        movements: set[tuple[int, int]] = set()

        if not isinstance(self._pieces[square], King):
            return movements

        # king-side castle
        target_king_square = (6, square[1])
        rook_column = 7
        if self.can_castle(square, target_king_square, (rook_column, square[1])):
            movements.add(target_king_square)

        # queen-side castle
        target_king_square = (2, square[1])
        rook_column = 0
        if self.can_castle(square, target_king_square, (rook_column, square[1])):
            movements.add(target_king_square)

        return movements

    def can_castle(
        self,
        king_square: tuple[int, int],
        target_king_square: tuple[int, int],
        rook_square: tuple[int, int],
    ):
        if king_square in self._pieces and isinstance(self._pieces[king_square], King):
            king: Piece = self._pieces[king_square]
        else:
            return False

        if rook_square in self._pieces and isinstance(self._pieces[rook_square], Rook):
            rook: Piece = self._pieces[rook_square]
        else:
            return False

        if self.is_king_in_check(king.is_white):
            return False

        if king.has_moved or rook.has_moved:
            return False

        # check if squares in-between are empty
        for column in range(
            min(king_square[0] + 1, rook_square[0] + 1), max(king_square[0], rook_square[0])
        ):
            if (column, king_square[1]) in self._pieces:
                return False

        # check if not castling through or into check
        for column in range(
            min(king_square[0] + 1, target_king_square[0]),
            max(king_square[0], target_king_square[0] + 1),
        ):
            movement: Movement = Movement(king_square, (column, king_square[1]))
            new_board: Board = self.move_piece(movement)
            if new_board.is_king_in_check(king.is_white):
                return False

        return True

    def is_king_in_check(self, is_white: bool) -> bool:
        king_square: tuple[int, int] = self._get_king_square(is_white)
        for square in self._pieces:
            if self._pieces[square].is_white != is_white:
                if king_square in self._pieces[square].get_moveable_squares(self._pieces, square):
                    return True
        return False

    def is_king_in_checkmate(self, is_white: bool) -> bool:
        if not self.is_king_in_check(is_white):
            return False

        for square in self._pieces:
            if self._pieces[square].is_white == is_white:
                if len(self.get_moveable_squares(square)) != 0:
                    return False

        return True

    def move_piece(self, movement: Movement) -> Board:
        new_board: Board = self.deep_clone()

        if movement.origin_square not in self._pieces:
            raise Exception(f"Piece not found at {movement.origin_square}")

        if isinstance(new_board._pieces[movement.origin_square], Pawn):
            new_board.pawn_movement(
                movement.origin_square, movement.target_square, movement.pawn_promotion
            )
        else:
            new_board.pawn_double_move = None

        if isinstance(new_board._pieces[movement.origin_square], King):
            new_board.king_movement(movement.origin_square, movement.target_square)

        # fifty move rule
        if isinstance(new_board._pieces[movement.origin_square], Pawn):
            new_board.halfmove_clock = 0
        elif movement.target_square in new_board._pieces:
            new_board.halfmove_clock = 0
        else:
            new_board.halfmove_clock += 1

        new_board._pieces[movement.origin_square].has_moved = True
        new_board._pieces[movement.target_square] = new_board._pieces[movement.origin_square]

        del new_board._pieces[movement.origin_square]

        if not new_board.white_turn:
            new_board.fullmove_number += 1

        new_board.white_turn = not new_board.white_turn

        return new_board

    def pawn_movement(
        self, pawn_square: tuple[int, int], target_square: tuple[int, int], promotion: Type[Piece]
    ):
        pawn: Piece = self._pieces[pawn_square]

        # promotion
        if pawn.is_white and target_square[1] == 0:
            self.promote_pawn(pawn_square, True, promotion)
        elif not pawn.is_white and target_square[1] == 7:
            self.promote_pawn(pawn_square, False, promotion)

        # track double move for 'en passant'
        if abs(pawn_square[1] - target_square[1]) == 2:
            self.pawn_double_move = target_square
        else:
            self.pawn_double_move = None

        # 'en passant' capture
        if abs(pawn_square[0] - target_square[0]) == 1:  # if capture
            if target_square not in self._pieces:  # if empty, must be 'en passant'
                direction = 1 if pawn.is_white else -1
                del self._pieces[(target_square[0], target_square[1] + direction)]

    def promote_pawn(self, square: tuple[int, int], is_white: bool, new_piece: Type[Piece] = Queen):
        self._pieces[square] = new_piece(is_white)
        self._pieces[square].has_moved = True

    def king_movement(self, king_square: tuple[int, int], target_square: tuple[int, int]):
        row = king_square[1]
        if abs(king_square[0] - target_square[0]) == 2:  # if castling
            if target_square[0] == 2:  # if queen-side-castle
                rook_square = (0, row)
                rook_target_square = (3, row)
            else:
                rook_square = (7, row)
                rook_target_square = (5, row)

            self._pieces[rook_target_square] = self._pieces[rook_square]  # move rook
            self._pieces[rook_target_square].has_moved = True
            del self._pieces[rook_square]

    def get_pieces(self) -> dict[tuple[int, int], Piece]:
        return self._pieces

    def set_pieces(self, pieces: dict[tuple[int, int], Piece]):
        self._pieces = pieces

    def deep_clone(self) -> Board:
        return copy.deepcopy(self)

    def fen_serialize(self) -> str:
        fen_strings: list[str] = [
            self._get_fen_piece_placements(),
            self._get_fen_active_color(),
            self._get_fen_castling_rights(),
            self._get_fen_en_passant_target(),
            self._get_fen_halfmove_clock(),
            self._get_fen_fullmove_clock(),
        ]
        return " ".join(fen_strings)

    def _get_fen_piece_placements(self) -> str:
        row_strings: list[str] = []
        for row in range(self.height):
            row_string: str = ""
            empty_counter: int = 0

            for column in range(self.width):
                if (column, row) in self._pieces:
                    if empty_counter != 0:
                        row_string += str(empty_counter)
                        empty_counter = 0
                    row_string += self._pieces[(column, row)].get_ascii_character()
                else:
                    empty_counter += 1

            if empty_counter > 0:
                row_string += str(empty_counter)

            row_strings.append(row_string)

        return "/".join(row_strings)

    def _get_fen_active_color(self) -> str:
        return "w" if self.white_turn else "b"

    def _get_fen_castling_rights(self) -> str:
        white_castling_rights: str = self._get_fen_castling_rights_for_color(is_white=True)
        black_castling_rights: str = self._get_fen_castling_rights_for_color(is_white=False)
        output: str = f"{white_castling_rights}{black_castling_rights}"

        if len(output) == 0:
            return "-"
        else:
            return output

    def _get_fen_castling_rights_for_color(self, is_white: bool) -> str:
        castling_rights: str = ""
        row: int = 7 if is_white else 0

        king_column = 4
        kingside_rook_column = 7
        queenside_rook_column = 0

        valid_king: bool = self._is_castling_piece_valid((king_column, row), King, is_white)
        valid_kingside_rook: bool = self._is_castling_piece_valid(
            (kingside_rook_column, row), Rook, is_white
        )
        valid_queenside_rook: bool = self._is_castling_piece_valid(
            (queenside_rook_column, row), Rook, is_white
        )

        if valid_king and valid_kingside_rook:
            castling_rights += "k"
        if valid_king and valid_queenside_rook:
            castling_rights += "q"

        if is_white:
            castling_rights = castling_rights.upper()

        return castling_rights

    def _is_castling_piece_valid(
        self, square: tuple[int, int], piece_class: Type[Piece], is_white: bool
    ):
        if square in self._pieces:
            piece: Piece = self._pieces[square]
            if isinstance(piece, piece_class):
                if piece.is_white == is_white and not piece.has_moved:
                    return True
        return False

    def _get_fen_en_passant_target(self) -> str:
        if self.pawn_double_move == None:
            return "-"
        else:
            pawn: Piece = self._pieces[self.pawn_double_move]
            direction: int = 1 if pawn.is_white else -1
            return self._square_to_algebraic(
                (self.pawn_double_move[0], self.pawn_double_move[1] + direction)
            )

    def _get_fen_halfmove_clock(self) -> str:
        return str(self.halfmove_clock)

    def _get_fen_fullmove_clock(self) -> str:
        return str(self.fullmove_number)

    def _square_to_algebraic(self, square: tuple[int, int]) -> str:
        """
        Converts square tuples to algebraic notation
        e.g. tuple(4, 2) -> "e6"
        """
        column: str = chr(square[0] + 97)  # 97 is code for 'a'
        row: str = str(8 - square[1])

        return f"{column}{row}"

    def _get_king_square(self, is_white: bool) -> tuple[int, int]:
        for square in self._pieces:
            piece: Piece = self._pieces[square]
            if isinstance(piece, King) and piece.is_white == is_white:
                return square
        raise Exception(f"King (white={is_white}) not found")
