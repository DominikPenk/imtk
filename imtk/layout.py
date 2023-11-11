from typing import Optional

from . import base
from .cursor import SameRowContext

__all__ = [
    'same_row',
    'row'
]

# Cursor methods
def same_row(context:Optional[base.ImContext]=None) -> None:
    """Ensure the next widget is placed in the same row as the previous one.

    Example:
    ```python
    imtk.button("First Button")
    imtk.same_row()
    imtk.button("Second Button")
    ```

    Args:
        context (Optional[base.ImFrame]): The active ImTk frame. If not provided, the current context will be used.
    """
    context = context or base.get_context()
    context.cursor.same_row()


def row(context:Optional[base.ImContext]=None) -> SameRowContext:
    """Start a new row for placing widgets.

    This function is used to begin a new row, allowing for the placement of multiple widgets
    horizontally in the layout.

    Example:
    ```python
    with imtk.row():
        imtk.button("Button 1")
        imtk.button("Button 2")
        imtk.button("Button 3")
    ```

    Args:
        context (Optional[base.ImFrame]): The context to use. If not provided, the current context will be used.

    Returns:
        SameRowContext: Context manager for managing the placement of widgets in the same row.
    """
    context = context or base.get_context()
    return context.cursor.row()