import sys

import click

from controller.game_config import GameConfig
from controller.game_controller import GameController


@click.command()
@click.option("-w", "--white", help="Path of chess engine to play white", type=str)
@click.option("-b", "--black", help="Path of chess engine to play black", type=str)
@click.option("-d", "--depth", default=25, help="Engine search depth, default 25", type=int)
@click.option("-a", "--ascii", default=False, is_flag=True, help="Use ASCII characters for pieces instead of NerdFont")
def main(white: str | None, black: str | None, depth: int, ascii: bool):
    """A simple Chess TUI program.

    Use arrow keys to move cursor, press 'Space' to confirm, 'Esc' to cancel and 'q' to quit.

    Engines used must be UCI compliant. If engines are not specified, player input will be used."""
    config: GameConfig = GameConfig(white, black, depth, ascii)
    controller: GameController = GameController(config)

    try:
        controller.start()
    except Exception as error:
        print(f"ERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
