from .cursor import ImCursor
from . import base
from .functional import _strip_label

__all__ = [
    'frame',
    'labelframe'
]

def frame(
    identifier:str,
    context: base.ImContext | None = None,
    **kwargs
) -> ImCursor:
    """
    Create a frame widget within the Immediate Mode GUI context and return a cursor for drawing in it.

    This function creates a frame widget, which is a container for grouping other widgets within
    the GUI.

    Args:
        identifier (str): A unique identifier for the frame widget.
        context (ImContext | None): The Immediate Mode GUI context in which the frame should be created.
            If not provided, the active context is used. (Default is None.)
        **kwargs: Additional keyword arguments to configure the frame widget.

    Returns:
        ImCursor: A cursor object for configuring and adding child widgets to the frame.

    Example:
        # Create a frame widget with the identifier "my_frame"
        with frame("my_frame"):
            # Within this block, all widget identifiers and actions are scoped to "my_frame"
            ...
    """
    # Create the widget and add it
    context = context or base.get_context()

    idx = context.get_identifier(identifier)
    info = context._widgets.get(idx, None)
    if info is None:
        info = base.ImWidgetState(
            widget = context.create_widget(
                'frame',
                **kwargs
            ),
            identifier=idx
        )

    frame_cursor = context.push_cursor()
    frame_cursor.frame = info

    return frame_cursor

def labelframe(
    label:str,
    context: base.ImContext | None = None,
    **kwargs
) -> ImCursor:
    """
    Create a labeled frame widget within the Immediate Mode GUI and return a cursor for configuring it.

    This function creates a labeled frame widget, which is a container with a title label for grouping
    other widgets within the GUI.

    Args:
        label (str): The text label to display on the labeled frame.
        context (ImContext | None): The Immediate Mode GUI context in which the labeled frame should
            be created. If not provided, the active context is used. (Default is None.)
        **kwargs: Additional keyword arguments to configure the labeled frame widget.

    Returns:
        ImCursor: A cursor object for configuring and adding child widgets to the labeled frame.

    Example:
        # Create a labeled frame widget with the label "Settings"
        with labelframe("Settings"):
            # Within this block, all widget identifiers and actions are scoped to "Settings"
            ...
    """
    # Create the widget and add it
    context = context or base.get_context()

    idx = context.get_identifier(label)
    info = context._widgets.get(idx, None)
    if info is None:
        info = base.ImWidgetState(
            widget = context.create_widget(
                'labelframe',
                text=_strip_label(label),
                **kwargs
            ),
            identifier=idx
        )

    frame_cursor = context.push_cursor()
    frame_cursor.frame = info
    frame_cursor._frame_end_padding += 15

    return frame_cursor
