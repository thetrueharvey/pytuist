"""
An actual test file.
"""
# %% Dependencies
# std
from pathlib import Path

# internal


def test_construct_test_hierarchy():
    from pytuist.pytuist import TestDir
    
    input = (Path("test") / "resources" / "example_pytest_output").with_suffix(".txt").read_text()

    tests = TestDir.from_pytest_output(input)

    tests

