"""
An actual test file.
"""
# %% Dependencies
# std
from pathlib import Path

# internal


def test_construct_test_hierarchy():
    from src.pytuist import TestDir
    
    input = (Path("test") / "resources" / "example_pytest_output").with_suffix(".txt").read_text()

    tests = TestDir.from_pytest_output(input)

    tests


def test_render():
    from src.pytuist import TestDir
    from src.render import render_test_tree
    
    input = (Path("test") / "resources" / "example_pytest_output").with_suffix(".txt").read_text()

    tests = TestDir.from_pytest_output(input)
    print()
    render_test_tree(tests)
