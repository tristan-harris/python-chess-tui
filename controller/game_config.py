class GameConfig:
    def __init__(
        self,
        white_engine_path: str | None,
        black_engine_path: str | None,
        engine_depth: int,
        ascii: bool,
    ):
        self.white_engine_path: str | None = white_engine_path
        self.black_engine_path: str | None = black_engine_path
        self.engine_depth: int = engine_depth
        self.ascii: bool = ascii

        if self.engine_depth <= 0:
            raise ValueError(f"Invalid engine depth of '{self.engine_depth}'")
