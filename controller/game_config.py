class GameConfig:
    def __init__(
        self,
        white_engine_path: str | None,
        black_engine_path: str | None,
        engine_depth: int,
        ascii: bool,
    ):
        self.white_engine_path = white_engine_path
        self.black_engine_path = black_engine_path
        self.engine_depth = engine_depth
        self.ascii = ascii
