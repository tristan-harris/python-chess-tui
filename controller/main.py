from model.board import Board
from view.game_view import GameView


class GameController:
    def __init__(self):
        self.board: Board = Board()
        self.board.setup_pieces()
        self.view: GameView = GameView(self.board)

    def run(self):
        self.view.run()
