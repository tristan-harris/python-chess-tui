import asyncio

from .game_config import GameConfig
from engine.uci_engine import UCIEngine
from model.board import Board
from model.movement import Movement
from view.game_view import GameView


class GameController:
    def __init__(self, config: GameConfig):
        self.config = config

        self.white_engine: UCIEngine | None = None
        if self.config.white_engine_path:
            self.white_engine = UCIEngine(self.config.white_engine_path, self.config.engine_depth)

        self.black_engine: UCIEngine | None = None
        if self.config.black_engine_path:
            self.black_engine = UCIEngine(self.config.black_engine_path, self.config.engine_depth)

        self.board: Board = Board()
        self.board.setup_pieces()
        self.view: GameView = GameView(self.board.deep_clone(), self.handle_movement, self.config)

    def start(self):
        asyncio.run(self.run_tasks())

    async def run_tasks(self):
        tasks: list[asyncio.Task] = []

        if self.white_engine:
            await self.white_engine.start()
            tasks.append(asyncio.create_task(self.white_engine.idle()))

        if self.black_engine:
            await self.black_engine.start()
            tasks.append(asyncio.create_task(self.black_engine.idle()))

        tasks.append(asyncio.create_task(self.setup_first_move()))

        await self.view.run()

    async def setup_first_move(self):
        # needed so that the view can draw the initial state of the board
        # before the movement made by an engine as white
        while not self.view.is_ready:
            await asyncio.sleep(0.1)

        if self.white_engine:
            movement: Movement = await self.get_engine_movement(self.white_engine)
            await self.handle_movement(movement)
        else:
            await self.view.enable_input()

    async def get_engine_movement(self, engine: UCIEngine) -> Movement:
        movement_text: str = await engine.get_move(self.board.fen_serialize())
        return Movement.create_from_algebraic(movement_text)

    async def handle_movement(self, movement: Movement):
        try:
            self.board = self.board.move_piece(movement)

            # fifty-move rule
            if self.board.halfmove_clock > 100:
                self.board.game_over = True
            if self.board.is_king_in_checkmate(self.board.white_turn):
                self.board.game_over = True

            await self.view.set_board(self.board.deep_clone())

            if self.board.game_over:
                await self.view.disable_input()
                return

            engine: UCIEngine | None = None

            if self.board.white_turn:
                if self.white_engine:
                    engine = self.white_engine
            else:
                if self.black_engine:
                    engine = self.black_engine

            if engine:
                await self.view.disable_input()
                next_movement: Movement = await self.get_engine_movement(engine)
                await self.handle_movement(next_movement)
            else:
                await self.view.enable_input()

        except asyncio.CancelledError:
            raise
