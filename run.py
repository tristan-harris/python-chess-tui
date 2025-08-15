import argparse
import sys

from controller.game_config import GameConfig
from controller.game_controller import GameController


def main():
    desc: str = (
        "A simple Chess TUI.\n\n"
        "Use arrow keys to move cursor, press 'Space' to confirm, 'Esc' to cancel and 'q' to quit.\n\n"
        "Engines used must be UCI compliant. If engine(s) are not specified, player input will be used."
    )
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=desc, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-w",
        "--white",
        dest="white_engine_path",
        type=str,
        help="Path of chess engine to play white",
        metavar="PATH",
    )
    parser.add_argument(
        "-b",
        "--black",
        dest="black_engine_path",
        type=str,
        help="Path of chess engine to play black",
        metavar="PATH",
    )
    parser.add_argument(
        "-d",
        "--depth",
        dest="engine_depth",
        default=25,
        type=int,
        help="Engine search depth, default 25",
        metavar="INTEGER",
    )
    parser.add_argument(
        "-a",
        "--ascii",
        dest="ascii",
        default=False,
        action="store_true",
        help="Use ASCII characters for pieces instead of NerdFont",
    )
    args: argparse.Namespace = parser.parse_args()

    config: GameConfig = GameConfig(**vars(args))  # pyright: ignore[reportAny]
    controller: GameController = GameController(config)

    try:
        controller.start()
    except Exception as error:
        print(f"ERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
