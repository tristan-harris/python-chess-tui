from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class Board:

    width = 8
    height = 8

    def __init__(self):
        self.pieces: dict[tuple[int, int], Piece] = {}

    def setup_pieces(self):
        self.pieces = {}

        for x in range(self.width):
            self.pieces[(x, 1)] = Pawn(True)
            self.pieces[(x, 6)] = Pawn(False)

        self.pieces[(0, 0)] = Rook(True)
        self.pieces[(1, 0)] = Knight(True)
        self.pieces[(2, 0)] = Bishop(True)
        self.pieces[(3, 0)] = Queen(True)
        self.pieces[(4, 0)] = King(True)
        self.pieces[(5, 0)] = Bishop(True)
        self.pieces[(6, 0)] = Knight(True)
        self.pieces[(7, 0)] = Rook(True)

        self.pieces[(0, 7)] = Rook(False)
        self.pieces[(1, 7)] = Knight(False)
        self.pieces[(2, 7)] = Bishop(False)
        self.pieces[(3, 7)] = Queen(False)
        self.pieces[(4, 7)] = King(False)
        self.pieces[(5, 7)] = Bishop(False)
        self.pieces[(6, 7)] = Knight(False)
        self.pieces[(7, 7)] = Rook(False)
