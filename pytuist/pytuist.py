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
from rich.tree import Tree

# internal

# %% Types
from typing import (
    Optional,
    Protocol,
)


# %% Folder Hierarchy
class Nav:
    """
    A class that defines navigation controls for a node in the test hierarchy.
    """
    owner: TestDir | Test

    def __init__(self, owner: TestDir | Test) -> None:
        self.owner = owner

    # Navigation-controls  # TODO: Account for being expanded or not
    def up(self) -> TestDir | Test:
        """
        Move to the previous child of the current node's parent (i.e. the neighbour above).
        """
        if self.owner.parent:
            index = self.owner.parent.children.index(self.owner)
            if index > 0:
                selected = self.owner.parent.children[index - 1]
                
                self.owner.renderer.unselect()
                selected.renderer.select()

                return selected

        return self.owner

    def down(self) -> TestDir | Test:
        """
        Move to the next child of the current node's parent (i.e. the neighbour below).
        """
        if self.owner.parent:
            index = self.owner.parent.children.index(self.owner)
            if index < len(self.owner.parent.children) - 1:
                selected = self.owner.parent.children[index + 1]
                
                self.owner.renderer.unselect()
                selected.renderer.select()

                return selected

        return self.owner

    def left(self) -> TestDir | Test:
        """
        Move into the parent
        """
        if self.owner.parent:
            self.owner.renderer.unselect()
            self.owner.parent.renderer.select()
            return self.owner.parent

        return self.owner

    def right(self) -> TestDir | Test:
        """
        Move into the first child
        """
        if isinstance(self.owner, TestDir) and len(self.owner.children) > 0:
            self.owner.renderer.unselect()
            self.owner.children[0].renderer.select()
            return self.owner.children[0]

        return self.owner

    def enter(self) -> TestDir | Test:
        """
        Expand or collapse the current node.
        """
        self.owner.renderer.toggle_expand()
        return self.owner


class TestDir:
    """
    A TestDir represents a directory that contains tests, or has children that contain tests.
    """
    _dir_registry: dict[str, TestDir] = {}

    name: str
    parent: Optional[TestDir] = None
    children: list[TestDir | Test]

    renderer: RenderConfig
    nav: Nav

    def __init__(self, name: str, parent: Optional[TestDir] = None) -> None:
        self.name = name
        self.parent = parent
        self.children = []

        self.__post_init__()

    def __post_init__(self) -> None:
        self._dir_registry[self.fully_qualified_path_str] = self
        if self.parent:
            self.parent.children.append(self)

        self.renderer = RenderConfig(self.name)
        self.nav = Nav(self)

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

        root: TestDir = TestDir(".")
        for module, functions in module_info.items():
            dir = cls._dir_registry[root.name]
                
            for part in module.split("/"):
                dir = dir.with_child(part)

            for function in functions:
                dir.with_test(function)

        if len(root.children) == 1 and isinstance(root.children[0], TestDir):
            root.children[0].parent = None
            root.children[0].renderer.select()
            return root.children[0]

        root.renderer.select()

        return root

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

    renderer: RenderConfig
    
    def __init__(self, name: str, parent: TestDir) -> None:
        self.name = name
        self.parent = parent

        self.__post_init__()

    def __post_init__(self):
        self.renderer = RenderConfig(self.name)
        self.nav = Nav(self)

    def __repr__(self) -> str:
        return "|" + ("-" * 4) * (self.parent.depth + 1) + f"> {self.name}"

    def __str__(self) -> str:
        return self.__repr__()


# %% Render Configuration
class RenderConfig:
    """
    Configuration for rendering a TestDir hierarchy.
    """
    name: str
    expanded: bool = True
    selected: bool = False

    def __init__(self, name: str):
        self.name = name

    def get_render(self) -> str:
        """
        Describes to rich how to render this object.
        """
        if self.selected:
            return f"[bold blue]{self.name}"
        
        return self.name

    def select(self) -> None:
        """
        Select this object.
        """
        self.selected = True

    def unselect(self) -> None:
        """
        Unselect this object.
        """
        self.selected = False

    def toggle_expand(self) -> None:
        """
        Expand or collapse this object.
        """
        self.expanded = not self.expanded


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

