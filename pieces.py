class Piece:

    name = "Piece"
    character = " "

    def __init__(self, white: bool):
        self.white = white
        self.name = "Piece"

    def __str__(self) -> str:
        return f"{self.name} (white={self.white})"


class Pawn(Piece):

    name = "Pawn"
    character = "󰡙"

    def __init__(self, white: bool):
        super().__init__(white)


class Knight(Piece):

    name = "Knight"
    character = "󰡘"

    def __init__(self, white: bool):
        super().__init__(white)


class Bishop(Piece):

    name = "Bishop"
    character = "󰡜"

    def __init__(self, white: bool):
        super().__init__(white)


class Rook(Piece):

    name = "Rook"
    character = "󰡛"

    def __init__(self, white: bool):
        super().__init__(white)


class Queen(Piece):

    name = "Queen"
    character = "󰡚"

    def __init__(self, white: bool):
        super().__init__(white)


class King(Piece):

    name = "King"
    character = "󰡗"

    def __init__(self, white: bool):
        super().__init__(white)
