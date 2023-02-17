"""
Automated demo that tests the low-level navigation and rendering functionality
"""
import sys
from pathlib import Path

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

 
if __name__ == "__main__":
    input = get_tests()

    root: TestDir = TestDir.from_pytest_output(input)
    selected: TestDir | Test = root

    console.clear()
    
    with Live(
        render_test_tree(root),
        console=console,
        refresh_per_second=60
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
                    selected.nav.space()

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
                    print(key)

            live.update(render_test_tree(root))
