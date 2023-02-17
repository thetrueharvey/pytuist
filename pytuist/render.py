"""
The rendering engine for pytuist.
"""
# %% Dependencies
# std

# external
from rich.tree import Tree
from rich.panel import Panel
from rich.layout import Layout

# internal
from pytuist.pytuist import TestDir


# %% Types


# %% Setup


# %% Render functions
def render_test_tree(test_hierarchy: TestDir):
    """
    Renders the test hierarchy
    """
    root = Tree(test_hierarchy.renderer.get_render())

    def _recursive_render(node: TestDir, parent: Tree):
        if node.renderer.expanded:
            for child in node.children:
                if isinstance(child, TestDir):
                    new_node = parent.add(child.renderer.get_render())
                    _recursive_render(child, new_node)
                else:  # We are at the leaf
                    parent.add(child.renderer.get_render())

    _recursive_render(test_hierarchy, root)

    hierarchy_render = Panel(
        root,
        title="pytuist",
        subtitle="arrows: navigate | enter: expand/collapse | space: run | q: quit",
        border_style="blue",
        subtitle_align="right",
        highlight=True,
        width=max(test_hierarchy.renderer._checkbox_position + 8, 80)
    )

    return hierarchy_render
