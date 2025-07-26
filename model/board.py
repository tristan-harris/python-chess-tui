from .pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class Board:

    width = 8
    height = 8

    def __init__(self):
        self._pieces: dict[tuple[int, int], Piece] = {}

    def get_pieces(self) -> dict[tuple[int, int], Piece]:
        return self._pieces

    def setup_pieces(self):
        self._pieces = {}

        # rows of pawns for both sides
        for x in range(self.width):
            self._pieces[(x, 1)] = Pawn(True)
            self._pieces[(x, 6)] = Pawn(False)

        # white
        self._pieces[(0, 0)] = Rook(True)
        self._pieces[(1, 0)] = Knight(True)
        self._pieces[(2, 0)] = Bishop(True)
        self._pieces[(3, 0)] = Queen(True)
        self._pieces[(4, 0)] = King(True)
        self._pieces[(5, 0)] = Bishop(True)
        self._pieces[(6, 0)] = Knight(True)
        self._pieces[(7, 0)] = Rook(True)

        # black
        self._pieces[(0, 7)] = Rook(False)
        self._pieces[(1, 7)] = Knight(False)
        self._pieces[(2, 7)] = Bishop(False)
        self._pieces[(3, 7)] = Queen(False)
        self._pieces[(4, 7)] = King(False)
        self._pieces[(5, 7)] = Bishop(False)
        self._pieces[(6, 7)] = Knight(False)
        self._pieces[(7, 7)] = Rook(False)

    def get_moveable_squares(self, square: tuple[int, int]) -> set[tuple[int, int]]:
        try:
            return self._pieces[square].get_moveable_squares(self._pieces, square)
        except:
            raise Exception(f"No piece found at {square}")

    def move_piece(self, piece_square: tuple[int, int], target_square: tuple[int, int]):
        self._pieces[piece_square].has_moved = True
        self._pieces[target_square] = self._pieces[piece_square]
        del self._pieces[piece_square]
