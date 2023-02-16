"""
Automated demo that tests the low-level navigation and rendering functionality
"""
import sys
from pathlib import Path

from pytuist.pytuist import TestDir
from pytuist.render import render_test_tree

from rich.live import Live
from rich.console import Console

import msvcrt

console = Console()

if __name__ == "__main__":
    input = (Path("test") / "resources" / "example_pytest_output").with_suffix(".txt").read_text()

    root = TestDir.from_pytest_output(input)
    selected = root

    console.clear()
    
    with Live(
        render_test_tree(root),
        console=console,
        refresh_per_second=60
    ) as live:
        while True:
            key = msvcrt.getch()

            if key in (b"q", b"\x03"):
                live.update("")
                sys.exit(0)

            if key == b"\r":
                selected.renderer.toggle_expand()

            if key == b"\xe0":
                key = msvcrt.getch()

                if key == b"H":
                    selected = selected.nav.up()

                if key == b"P":
                    selected = selected.nav.down()

                if key == b"M":
                    selected = selected.nav.right()

                if key == b"K":
                    selected = selected.nav.left()

            live.update(render_test_tree(root))
