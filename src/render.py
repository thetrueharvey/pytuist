"""
The rendering engine for pytuist.
"""
# %% Dependencies
# std

# external
from rich.tree import Tree
from rich.panel import Panel
from rich.console import Group
from rich.columns import Columns

# internal
from src.pytuist import TestDir


# %% Types
from typing import Optional


# %% Setup


# %% Render functions
def render_test_tree(
    test_hierarchy: TestDir,
    pytest_output: Optional[str] = None,
):
    """
    Renders the test hierarchy
    """
    checkbox_position = test_hierarchy.renderer.get_checkbox_position()

    root = Tree(test_hierarchy.renderer.get_render(checkbox_position))

    def _recursive_render(node: TestDir, parent: Tree):
        if node.renderer.expanded:
            for child in node.children:
                if isinstance(child, TestDir):
                    new_node = parent.add(child.renderer.get_render(checkbox_position))
                    _recursive_render(child, new_node)
                else:  # We are at the leaf
                    parent.add(child.renderer.get_render(checkbox_position))

    _recursive_render(test_hierarchy, root)

    header = Panel(
        "[bold green]arrows[/bold green]: navigate | "
        "[bold green]enter[/bold green]: expand/collapse | "
        "[bold green]space[/bold green]: run | "
        "[bold green]q[/bold green]: quit",
        title="pytuist",
        width=144 + checkbox_position + 8,
    )

    hierarchy_panel = Panel(
        root,
        title="Tests",
        border_style="blue",
        width=checkbox_position + 8
    )

    if pytest_output is None:
        output_style = "white"
    else:
        output_style = "red" if "failed" in pytest_output else "green"

    output_panel = Panel(
        pytest_output or "[italic]Run a test to see the output here",
        title="Output",
        width=143,
        border_style=output_style
    )

    return Group(
        header,
        Columns([hierarchy_panel, output_panel]),
        fit=True
    )
