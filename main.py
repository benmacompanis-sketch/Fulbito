"""Punto de entrada: `python main.py [archivo.json]`."""

import sys
from pathlib import Path

from futbol.cli import App
from futbol.storage import load_state

DEFAULT_FILE = Path(__file__).with_name("datos.json")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    App(load_state(path), path).run()
    print("¡Nos vemos en la cancha!")


if __name__ == "__main__":
    main()
