import tkinter as tk
from functools import update_wrapper, wraps
from typing import Any, Callable, Optional, Sequence, Tuple, Type

from . import base
from .base import ImWidgetState

__all__ = [
    'same_row',
    'row',

    'button',
    'checkbox',
    'combo_box',
    'text',
    'input_text',
    'input_int',
    'input_float',
    'float_slider',
    'int_slider',
    'progress_bar',
    'horizontal_separator'
]


class _Callback(object):
    def __init__(self, fn):
        self.active = True
        self.fn = fn

    def __call__(self, *args, **kwargs):
        if self.active:
            self.fn(*args, **kwargs)


def _strip_label(label:str):
    """For widgets with text labels we strip everything after the first '#'"""
    return label.split("#")[0]


# Cursor methods
def same_row(context:Optional[base.ImContext]=None):
    """Ensure the next widget is placed in the same row as the previous one.

    Args:
        context (Optional[base.ImFrame]): The active ImTk frame.
    """
    context = context or base.get_context()
    context.cursor.same_row()


def row(context:Optional[base.ImContext]=None):
    """Start a new row for placing widgets.
    
    Args:
        context (Optional[base.ImFrame]): The Immediate Mode GUI frame context.
    """
    context = context or base.get_context()
    return context.cursor.row()


def imtk_widget(draw_fn=None):
    def _wrapper(info_fn):
        @wraps(info_fn)
        def wrapped_function(*args, **kwargs):
            info_ret = info_fn(*args, **kwargs)
            info = info_ret[0] if isinstance(info_ret, Sequence) else info_ret

            context: base.ImContext = base.get_context()
            wrapped_function.draw(info, context)

            info._active = context.active_widget == info.identifier
            return info_ret
        
        if draw_fn is None:
            def default_draw_fn(info, context):
                context.cursor.add_widget(info)
            wrapped_function.draw = default_draw_fn
        else:
            wrapped_function.draw = draw_fn

        return wrapped_function
    return _wrapper


def _draw_widget_with_label(info:ImWidgetState, context:base.ImContext):
    label_text:str = info.custom_data['label_text']
    label_first:bool = info.custom_data['label_first']

    with context.cursor.row():
        if label_text and label_first:
            text(text=label_text, identifier=f"{info.identifier}#label")

        context.cursor.add_widget(info, context)
    
        if not label_first and label_text:
            text(text=_strip_label(label_text), identifier=f"{info.identifier}#label")


@imtk_widget()
def text(text:str, identifier:Optional[str]=None) -> ImWidgetState:
    """Create a text widget.

    Args:
        text (str): The text to display.
        identifier (Optional[str]): An optional identifier for the widget. If None the text itself is used as an identifier.

    Returns:
        ImWidgetState: The state of the created text widget.
    """
    context = base.get_context()

    idx = context.get_identifier(identifier if identifier else text)
    info = context._widgets.get(idx, None)
    if info is None:
        data = { 'text': tk.StringVar(value=text) }
        info = ImWidgetState(
            context.create_widget(
                'label',
                textvariable=data['text']
            ),
            idx,
            custom_data=data
        )

    info.custom_data.get("text").set(text)
    return info


@imtk_widget()
def button(text:str, **kwargs:dict[str, Any]) -> ImWidgetState:
    """A simple button widget.

    Example:
    ```python
    if imtk.button("A Button"):
        print("Button was pressed")
    ```

    Args:
        text (str): Text on the button

    Keyword Args:
        **kwargs: These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.button.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/button.html).
    
    Note:
        You should never manually set the following arguments: *parent, text and command*

    Returns:
        ImWidgetState: State of the widget. Can be used as a boolean to check if it was clicked. 
    """
    context = base.get_context()
    
    idx = context.get_identifier(text)
    state = context._widgets.get(idx, None)
    if state is None:
        state = ImWidgetState(
            context.create_widget(
                'button',
                text=_strip_label(text),
                command=lambda: context.set_active(idx),
                **kwargs
            ),
            idx
        )
    return state


@imtk_widget()
def checkbox(label:str, value:bool, **kwargs) -> Tuple[ImWidgetState, bool]:
    context = base.get_context()

    idx = context.get_identifier(label)
    info = context._widgets.get(idx, None)
    if info is None:
        data = { 'state': tk.IntVar() }
        info = ImWidgetState(
            context.create_widget(
                'checkbutton',
                text=label,
                variable=data['state'],
                command=lambda: context.set_active(label),
                **kwargs
            ),
            idx,
            custom_data=data
        )
    if context.active_widget != info.identifier:
        info.custom_data['state'].set(value)

    return info, info.custom_data['state'].get() == 1

# Textbox inputs

@imtk_widget(draw_fn=_draw_widget_with_label)
def input_text(label:str, text_:str, label_position:str='right', **kwargs) -> Tuple[ImWidgetState, str]:
    """A input box for strings"""
    if label_position not in ['right', 'left', 'r', 'l', 'west', 'w', 'east', 'e']:
        raise ValueError("label_position must be in one of 'right', 'left', 'r', 'l', 'west', 'w', 'east' or 'e'")
    context = base.get_context()

    idx = context.get_identifier(label)
    info = context._widgets.get(idx, None)
    
    if info is None:
        data = {
            'value': tk.StringVar(value=text_),
            'callback': _Callback(
                lambda *args: context.set_active(info.identifier),
            )
        }
        input = context.create_widget(
            'entry',
            textvariable=data['value'],
            **kwargs
        )
        # Create the widget
        info = ImWidgetState(
            input,
            idx,
            custom_data=data
        )
        data['value'].trace_add("write", data['callback'])

    info.custom_data.update({
        'label_first': label_position in ['left', 'west', 'l', 'w'],
        'label_text': _strip_label(label)
    })
    

    if context.active_widget != info.identifier:
        info.custom_data['callback'].active = False
        info.custom_data['value'].set(text_)
        info.custom_data['callback'].active = True

    return info, info.custom_data['value'].get()


def _spinbox(
    string_to_val:Callable[[str], Any],
    val_to_string:Callable[[Any], str],
    label:str,
    val:int|float,
    vmin:int|float,
    vmax:int|float,
    label_position:str='right',
    **kwargs
) -> Tuple[ImWidgetState, float | int]:
    if label_position not in ['right', 'left', 'r', 'l', 'west', 'w', 'east', 'e']:
        raise ValueError("label_position must be in one of 'right', 'left', 'r', 'l', 'west', 'w', 'east' or 'e'")
    context = base.get_context()

    idx = context.get_identifier(label)
    info = context._widgets.get(idx, None)

    if info is None:
        data = {
            'value': tk.StringVar(value=val),
            'callback': _Callback(
                lambda *args: context.set_active(info.identifier)
            )
        }
        input = context.create_widget(
            'spinbox',
            textvariable=data['value'],
            from_=vmin,
            to=vmax,
            **kwargs
        )
        # Create the widget
        info = ImWidgetState(
            input,
            idx,
            custom_data=data
        )
        data['value'].trace_add("write", data['callback'])

    info.custom_data.update({
        'label_text': _strip_label(label),
        'label_first': label_position in ['left', 'west', 'l', 'w'] 
    })

    if context.active_widget != info.identifier:
        info.custom_data['callback'].active = False
        info.custom_data['value'].set(val_to_string(val))
        info.custom_data['callback'].active = True


    return info, string_to_val(info.custom_data['value'].get())


@imtk_widget(draw_fn=_draw_widget_with_label)
def input_int(
    label:str,
    val:int,
    vmin:int=0,
    vmax:int=100,
    label_position:str='right',
    **kwargs
) -> Tuple[ImWidgetState, int]:
    return _spinbox(
        string_to_val=int,
        val_to_string=str,
        label=label,
        val=val,
        vmin=vmin,
        vmax=vmax,
        label_position=label_position,
        **kwargs
    )


@imtk_widget(draw_fn=_draw_widget_with_label)
def input_float(
    label:str,
    val:float,
    vmin:float=0,
    vmax:float=100,
    label_position:str='right',
    format_:str="%.3f",
    increment:float=0.1,
    **kwargs
) -> Tuple[ImWidgetState, float]:
    return _spinbox(
        string_to_val=lambda v: float(v.replace(",", ".")),
        val_to_string=lambda v: format_ % v,
        label=label,
        val=val,
        vmin=vmin,
        vmax=vmax,
        label_position=label_position,
        format=format_,
        increment=increment,
        **kwargs
    )

# Slider Inputs

def _slider(
    label, 
    val,
    VarType:Type[tk.Variable], 
    vmin, 
    vmax, 
    label_position, 
    **kwargs
) -> Tuple[ImWidgetState, float | int]:
    if label_position not in ['right', 'left', 'r', 'l', 'west', 'w', 'east', 'e']:
        raise ValueError("label_position must be in one of 'right', 'left', 'r', 'l', 'west', 'w', 'east' or 'e'")
    context = base.get_context()

    idx = context.get_identifier(label)
    info = context._widgets.get(idx, None)

    
    if info is None:
        data = {
            'value': VarType(value=val),
            'callback': _Callback(
                lambda *args: context.set_active(info.identifier)
            )
        }
        input = context.create_widget(
            'scale',
            var=data['value'],
            from_=vmin,
            to=vmax,
            **kwargs
        )
        # Create the widget
        info = ImWidgetState(
            input,
            idx,
            custom_data=data
        )
        data['value'].trace_add("write", data['callback'])

    info.custom_data.update({
        'label_first': label_position in ['left', 'west', 'l', 'w'],
        'label_text': _strip_label(label)
    })


    if context.active_widget != info.identifier:
        info.custom_data['callback'].active = False
        info.custom_data['value'].set(val)
        info.custom_data['callback'].active = True

    return info, info.custom_data['value'].get()


@imtk_widget(draw_fn=_draw_widget_with_label)
def float_slider(
    label:str,
    val:float,
    vmin:float=0.0,
    vmax:float=1.0,
    label_position:str='right',
    **kwargs
) -> Tuple[ImWidgetState, float]:
    return _slider(
        label=label, 
        val=val, 
        VarType=tk.DoubleVar, 
        vmin=vmin, 
        vmax=vmax, 
        label_position=label_position, 
        **kwargs
    )


@imtk_widget(draw_fn=_draw_widget_with_label)
def int_slider(
    label:str,
    val:int,
    vmin:int=0,
    vmax:int=100,
    label_position:str='right',
    **kwargs
) -> Tuple[ImWidgetState, int]:
    return _slider(
        label=label, 
        val=val, 
        VarType=tk.IntVar, 
        vmin=vmin, 
        vmax=vmax, 
        label_position=label_position, 
        **kwargs
    )


@imtk_widget(draw_fn=_draw_widget_with_label)
def combo_box(
    label:str,
    current_index:int,
    values:Sequence[str],
    label_position:str='right',
    **kwargs
) -> Tuple[ImWidgetState, int]:
    context = base.get_context()
    idx     = context.get_identifier(label)

    info = context._widgets.get(idx, None)
    if info is None:
        label = _strip_label(label)
        box = context.create_widget(
            'combobox',
            **kwargs
        )
        data = {
            'callback': _Callback(
                lambda *args: context.set_active(info.identifier)
            )
        }
        box['state'] = 'readonly'
        # Create the widget
        info = ImWidgetState(
            box,
            idx,
            custom_data=data
        )
        box.bind('<<ComboboxSelected>>', data['callback'])

    info.widget['values'] = values 
    info.custom_data.update({
        'label_first': label_position in ['left', 'west', 'l', 'w'],
        'label_text': _strip_label(label)
    })
    
    if context.active_widget != info.identifier:
        info.custom_data['callback'].active = False
        info.widget.current(current_index)
        info.custom_data['callback'].active = True

    return info, info.widget.current()


def progress_bar_draw(
    info:ImWidgetState,
    context:base.ImContext
) -> None:
    label_text:str = info.custom_data['label_text']
    label_first:bool = info.custom_data['label_first']
    show_progress:bool = info.custom_data['show_progress']

    with context.cursor.row():
        if label_text and label_first:
            text(text=label_text, identifier=f"{info.identifier}#label")

        context.cursor.add_widget(info, context)
    
        if show_progress:
            text(text=f"{info.custom_data['progress'].get()}%", identifier=f"{info.identifier}#progress")

        if not label_first and label_text:
            text(text=_strip_label(label_text), identifier=f"{info.identifier}#label")

@imtk_widget(draw_fn=progress_bar_draw)
def progress_bar(
    label:str, 
    value:float, 
    min_:float=0.0,
    max_:float=1.0,
    label_position:str='right',
    show_progress:bool=False,
    **kwargs
):
    """This progressbar will not return the given value"""
    context = base.get_context()

    idx = context.get_identifier(label)
    info = context._widgets.get(idx, None)

    
    if info is None:
        var = tk.IntVar()
        bar = context.create_widget(
            'progressbar',
            variable=var,
            **kwargs
        )

        # Create the widget
        info = ImWidgetState(
            bar,
            idx,
            custom_data={
                'progress': var
            }
        )


    t = max(0, min(1, (value - min_) / (max_ - min_)))
    info.custom_data['progress'].set(int(t * 100))

    info.custom_data.update({
        'label_first': label_position in ['left', 'west', 'l', 'w'],
        'label_text': _strip_label(label),
        'show_progress': show_progress,
    })
    
    return info


def horizontal_separator_draw(info:ImWidgetState, context:base.ImContext):
    cursor = context.cursor
    cursor.add_widget(info, context, **info.custom_data)

@imtk_widget(draw_fn=horizontal_separator_draw)
def horizontal_separator(identifier:str, width:int=None, relwidth:float=0.95, **kwargs):
    context = base.get_context()

    idx = context.get_identifier(identifier)
    info = context._widgets.get(idx, None)

        
    if info is None:
        kwargs.update({
            'orient': 'horizontal'
        })
        separator = context.create_widget(
            'separator',
            **kwargs
        )

        # Create the widget
        info = ImWidgetState(separator, idx)

    info.custom_data.update({
        'width': width,
        'relwidth': relwidth
    })
    return info
