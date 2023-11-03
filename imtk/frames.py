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
