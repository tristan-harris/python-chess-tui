import asyncio
from pathlib import Path


class UCIEngineError(Exception):
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
            raise UCIEngineError(f"Engine not found at '{self.path}'")
        except PermissionError:
            raise UCIEngineError(f"Permission denied for executing engine '{self.path}'")
        except asyncio.TimeoutError:
            raise UCIEngineError(f"Subprocess for engine '{self.path}' timed-out")
        except OSError:
            raise UCIEngineError(f"Unexpected OS error starting engine '{self.path}'")
        except Exception:
            raise UCIEngineError(f"Unexpected error starting engine '{self.path}'")

        if self.process.stdin is None:
            raise UCIEngineError(f"Could not create stdin pipe for engine '{self.path}'")
        if self.process.stdout is None:
            raise UCIEngineError(f"Could not create stdout pipe for engine '{self.path}'")

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
            await self.terminate()
            raise UCIEngineError(f"Engine '{self.path}' did not respond to UCI initialisation")

    async def idle(self):
        try:
            while True:
                await asyncio.sleep(100_000)
        except asyncio.CancelledError:
            await self.terminate()
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

    async def terminate(self):
        if self.process:
            try:
                await self.write("quit")
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except (asyncio.TimeoutError, OSError):
                self.process.kill()
                await self.process.wait()
