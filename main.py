"""
The main entrypoint for pytuist
"""
import sys

from pytuist.pytuist import (
    TestDir,
    Test,
    get_tests,
)
from pytuist.render import render_test_tree

from rich.live import Live
from rich.console import Console

import msvcrt

console = Console()

def main():
    input = get_tests()

    root: TestDir = TestDir.from_pytest_output(input)
    selected: TestDir | Test = root

    output = None

    console.clear()
    
    with Live(
        render_test_tree(root),
        console=console,
        refresh_per_second=120
    ) as live:
        while True:
            key = msvcrt.getch()

            match key:
                case b"q" | b"\x03":
                    live.update("")
                    sys.exit(0)

                case b"\r":
                    selected.nav.enter()

                case b" ":
                    _, output = selected.nav.space()

                case b"\xe0":
                    key = msvcrt.getch()
                    match key:
                        case b"H":
                            selected = selected.nav.up()
                        case b"P":
                            selected = selected.nav.down()
                        case b"M":
                            selected = selected.nav.right()
                        case b"K":
                            selected = selected.nav.left()
                        case _:
                            pass
                case _:
                    pass

            live.update(render_test_tree(root, output), refresh=True)
 
if __name__ == "__main__":
    main()
