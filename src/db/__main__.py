# src/db/__main__.py
from .tui import BookUI


def main() -> None:
    ui = BookUI()
    ui.run()


if __name__ == "__main__":
    main()