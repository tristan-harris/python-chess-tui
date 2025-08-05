import asyncio
from pathlib import Path


class UCIEngineError(Exception):
    pass


class UCIEngineStartupError(UCIEngineError):
    pass


class UCIEngineTimeoutError(UCIEngineError):
    pass


class UCIEngine:
    def __init__(self, path: str, depth: int):
        self.path: Path = Path(path)
        self.depth: int = depth

    async def start(self):
        try:
            self.process: asyncio.subprocess.Process = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    program=self.path.resolve(),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                ),
                timeout=5,
            )
        except FileNotFoundError:
            raise UCIEngineStartupError(f"Engine not found at '{self.path}'")
        except PermissionError:
            raise UCIEngineStartupError(f"Permission denied for executing engine '{self.path}'")
        except asyncio.TimeoutError:
            raise UCIEngineStartupError(f"Subprocess for engine '{self.path}' timed-out")
        except OSError:
            raise UCIEngineStartupError(f"Unexpected OS error starting engine '{self.path}'")
        except Exception:
            raise UCIEngineStartupError(f"Unexpected error starting engine '{self.path}'")

        if self.process.stdin is None:
            raise UCIEngineStartupError(f"Could not create stdin pipe for engine '{self.path}'")
        if self.process.stdout is None:
            raise UCIEngineStartupError(f"Could not create stdout pipe for engine '{self.path}'")

        self.stdin: asyncio.StreamWriter = self.process.stdin
        self.stdout: asyncio.StreamReader = self.process.stdout

        await self._initialize_uci()

    async def _initialize_uci(self, timeout: float = 3):
        try:
            await asyncio.wait_for(self.write("uci"), timeout=timeout)
            await asyncio.wait_for(self.wait_for("uciok"), timeout=timeout)
            await asyncio.wait_for(self.write("ucinewgame"), timeout=timeout)
            await asyncio.wait_for(self.write("isready"), timeout=timeout)
            await asyncio.wait_for(self.wait_for("readyok"), timeout=timeout)
        except asyncio.TimeoutError:
            raise UCIEngineTimeoutError(f"Engine '{self.path}' did not respond to UCI initialisation")

    async def idle(self):
        try:
            while True:
                await asyncio.sleep(100_000)
        except asyncio.CancelledError:
            await self.quit()
            raise

    async def write(self, command: str):
        self.stdin.write((command + "\n").encode())
        await self.stdin.drain()

    async def read_line(self) -> str:
        line_bytes: bytes = await self.stdout.readline()
        return line_bytes.decode().rstrip()

    async def wait_for(self, text: str) -> str:
        while True:
            line: str = await self.read_line()
            if line.startswith(text):
                return line

    async def get_move(self, fen_text: str) -> str:
        await self.write(f"position fen {fen_text}")
        await self.write(f"go depth {self.depth}")
        output: str = await self.wait_for("bestmove")
        move: str = output.split(" ")[1]
        return move

    async def quit(self):
        try:
            await self.write("quit")
            await self.process.wait()
        except Exception:
            self.process.kill()
