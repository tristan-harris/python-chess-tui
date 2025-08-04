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

        self.view: GameView = GameView(self.board.deep_clone(), self.handle_human_movement, self.config)

        self.movements_queue: list[Movement] = []

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

        tasks.append(asyncio.create_task(self.process_movements()))

        await self.view.run()

    async def process_movements(self):
        try:
            # needed so that the view can draw the initial state of the board
            # before the movement made by an engine as white
            while not self.view.is_ready:
                await asyncio.sleep(0.1)

            # setup first move
            if self.white_engine:
                self.movements_queue.append(await self.get_engine_movement(self.white_engine))
            else:
                await self.view.enable_input()

            while True:
                if len(self.movements_queue) == 0:
                    await asyncio.sleep(0.01)
                    continue

                movement: Movement = self.movements_queue.pop(0)
                self.board = self.board.move_piece(movement)

                # fifty-move rule
                if self.board.halfmove_clock > 100:
                    self.board.game_over = True
                elif self.board.is_king_in_checkmate(self.board.white_turn):
                    self.board.game_over = True

                await self.view.set_board(self.board.deep_clone())

                if self.board.game_over:
                    await self.view.disable_input()
                    break

                engine: UCIEngine | None = None

                if self.board.white_turn and self.white_engine:
                    engine = self.white_engine
                elif not self.board.white_turn and self.black_engine:
                    engine = self.black_engine

                if engine:
                    await self.view.disable_input()
                    self.movements_queue.append(await self.get_engine_movement(engine))
                else:
                    await self.view.enable_input()

        except asyncio.CancelledError:
            raise

    async def get_engine_movement(self, engine: UCIEngine) -> Movement:
        movement_text: str = await engine.get_move(self.board.fen_serialize())
        return Movement.create_from_algebraic(movement_text)

    async def handle_human_movement(self, movement: Movement):
        self.movements_queue.append(movement)
