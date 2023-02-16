from pathlib import Path

from pytuist.pytuist import TestDir
from pytuist.render import render_test_tree

if __name__ == "__main__":
    input = (Path("test") / "resources" / "example_pytest_output").with_suffix(".txt").read_text()

    tests = TestDir.from_pytest_output(input)

    tests.children[0].renderer.selected = True
    
    print()
    render_test_tree(tests)
