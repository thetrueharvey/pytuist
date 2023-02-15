"""
The core of pytuist, currently more of a scratch file for getting basically functionalty working.
"""
# %% Dependencies
from __future__ import annotations

# std
import subprocess
from pathlib import Path
import re

# external

# internal

# %% Types
from typing import (
    Optional,
)


# %% Folder Hierarchy
class TestDir:
    """
    A TestDir represents a directory that contains tests, or has children that contain tests.
    """
    _dir_registry: dict[str, TestDir] = {}

    name: str
    parent: Optional[TestDir] = None
    children: list[TestDir | Test]

    def __init__(self, name: str, parent: Optional[TestDir] = None) -> None:
        self.name = name
        self.parent = parent
        self.children = []

        self.__post_init__()

    def __post_init__(self) -> None:
        self._dir_registry[self.fully_qualified_path_str] = self
        if self.parent:
            self.parent.children.append(self)

    def with_child(self, name: str) -> TestDir:
        """
        Create a child TestDir with the given name.
        """
        if f"{self.fully_qualified_path_str}/{name}" in self._dir_registry:
            return self._dir_registry[self.fully_qualified_path_str + "/" + name]

        child = TestDir(name, parent=self)
        return child

    def with_test(self, name: str) -> Test:
        """
        Create a child Test with the given name.
        """
        child = Test(name, self)
        self.children.append(child)
        return child

    @property
    def fully_qualified_path_str(self) -> str:
        """
        The full path of the TestDir, including all parents.
        """
        return self.parent.fully_qualified_path_str + "/" + self.name if self.parent else self.name

    @property
    def fully_qualified_path_list(self) -> list[str]:
        return self.parent.fully_qualified_path_list + [self.name] if self.parent else [self.name]

    @property
    def depth(self) -> int:
        return len(self.fully_qualified_path_list) - 1

    @classmethod
    def from_pytest_output(cls, pytest_output: str) -> TestDir:
        """
        Construct a TestDir hierarchy from the output of pytest --collect-only.
        """
        module_pattern = re.compile(r'<Module\s+(.*)>')
        function_pattern = re.compile(r'<Function\s+(.*)>')

        module_info: dict[str, list[str]] = {}
        current_module = None
        for line in pytest_output.splitlines():
            match = module_pattern.search(line)
            if match:
                current_module = match.group(1)
                module_info[current_module] = []
            else:
                match = function_pattern.search(line)
                if match and current_module is not None:
                    module_info[current_module].append(match.group(1))
  
        for module, functions in module_info.items():
            root = module.split("/")[0]
            if root not in cls._dir_registry:
                dir = TestDir(root)
            else:
                dir = cls._dir_registry[root]
                
            for part in module.split("/")[1:]:
                dir = dir.with_child(part)

            for function in functions:
                dir.with_test(function)
        
        return cls._dir_registry[root]  # TODO: Handle this case

    def __repr__(self) -> str:
        if self.parent:
            self_repr = "|" + ("-" * 4) * self.depth + f"[{self.name}]\n"
        else:
            self_repr = f"[{self.name}]\n"
        return self_repr + "\n".join([repr(child) for child in self.children])

    def __str__(self) -> str:
        return self.__repr__()


class Test:
    """
    A Test represents a single test, the leaf of a Hierachy of TestDirs.
    """
    name: str
    parent: TestDir
    
    def __init__(self, name: str, parent: TestDir) -> None:
        self.name = name
        self.parent = parent

    def __repr__(self) -> str:
        return "|" + ("-" * 4) * (self.parent.depth + 1) + f"> {self.name}"

    def __str__(self) -> str:
        return self.__repr__()


# %% Functions
def get_tests(root_dir: Path = Path.cwd()):
    """
    Get all the tests that pytest can find.
    """
    pytest_output = subprocess.run(
        ["pytest", "--collect-only"],
        cwd=root_dir,
        capture_output=True
    )

    return pytest_output.stdout.decode("utf-8")

