import tkinter as tk
from functools import wraps
from typing import Any, Callable, Optional, Sequence, Tuple, Type

from . import base
from .base import ImWidgetState

__all__ = [
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
        state: State of the widget. Can be used as a boolean to check if it was clicked. 
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
    """A checkbox widget.

    Example:
    ```python
    checked, current_value = imtk.checkbox("Enable Feature", value=True)
    if checked:
        print("Feature is enabled")
    ```

    Args:
        label (str): The label associated with the checkbox.
        value (bool): The initial state of the checkbox.

    Keyword Args:
        **kwargs: Additional keyword arguments to customize the checkbox.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.checkbox.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/checkbutton.html).
            
    Note: 
        You should never manually set the following arguments: *parent, text, and command*.

    Returns:
        - ImWidgetState: State of the widget. Can be used as a boolean to check if the checkbox state was modified.
        - bool: The current state of the checkbox (checked or unchecked).
    """
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
    """A widget to input text
    
    Example:
    ```python
    current_value = "Some Text"

    changed, current_value = imtk.input_text(label="Text Input", text_=Some text)
    if changed:
        print("The text changed to", current_value)
    ```

    Args:
        label (str): The label associated with the text input field.
        text_ (str): The current text value displayed in the input field.

    Keyword Args:
        label_position (str, optional): The position of the label relative to the input field.
            Possible values: 'left', 'right'. Defaults to 'right'.
        **kwargs: Additional keyword arguments to customize the text input field.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.input_text.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry.html).
    
    Note: 
        You should never manually set the following arguments: *parent, text, and command*.

    Returns:
        state: State of the widget. Can be used as a boolean to check if the text was modified.
        value: The current text value in the input field. 
    """
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
    """A widget for inputting integer values within a specified range.

    Example:
    ```python
    changed, current_value = imtk.input_int(label="Set Value", val=current_value, vmin=0, vmax=100)
    if changed:
        print("The value changed to", current_value)
    ```

    Args:
        label (str): The label associated with the integer input field.
        val (int): The initial integer value displayed in the input field.

    Keyword Args:
        vmin (int, optional): The minimum allowed value. Defaults to 0.
        vmax (int, optional): The maximum allowed value. Defaults to 100.
        label_position (str, optional): The position of the label relative to the input field.
            Possible values: 'left', 'right'. Defaults to 'right'.
        **kwargs: Additional keyword arguments to customize the integer input field.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.input_int.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry.html).
            
    Note: 
        You should never manually set the following arguments: *parent, text, and command*.

    Returns:
        state: State of the widget. Can be used as a boolean to check if the value was modified.
        int: The current integer value in the input field.
    """
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
    """A widget for inputting floating-point values within a specified range.

    Example:
    ```python
    changed, current_value = imtk.input_float(label="Set Value", val=current_value, vmin=0, vmax=100, increment=0.1)
    if changed:
        print("The value changed to", current_value)
    ```

    Args:
        label (str): The label associated with the floating-point input field.
        val (float): The initial floating-point value displayed in the input field.

    Keyword Args:
        vmin (float, optional): The minimum allowed value. Defaults to 0.
        vmax (float, optional): The maximum allowed value. Defaults to 100.
        label_position (str, optional): The position of the label relative to the input field.
            Possible values: 'left', 'right'. Defaults to 'right'.
        format_ (str, optional): The format string used to display the floating-point value. Defaults to "%.3f".
        increment (float, optional): The increment step for the input field. Defaults to 0.1.
        **kwargs: Additional keyword arguments to customize the floating-point input field.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.input_float.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry.html).
            
    Note: 
        You should never manually set the following arguments: *parent, text, and command*.

    Returns:
        state: State of the widget. Can be used as a boolean to check if the value was modified.
        float: The current floating-point value in the input field.
    """
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
    """A slider widget for selecting floating-point values within a specified range.

    Example:
    ```python
    changed, current_value = imtk.float_slider(label="Adjust Value", val=current_value, vmin=0.0, vmax=1.0)
    if changed:
        print("The value changed to", current_value)
    ```

    Args:
        label (str): The label associated with the float slider.
        val (float): The initial floating-point value displayed on the slider.

    Keyword Args:
        vmin (float, optional): The minimum allowed value. Defaults to 0.0.
        vmax (float, optional): The maximum allowed value. Defaults to 1.0.
        label_position (str, optional): The position of the label relative to the slider.
            Possible values: 'left', 'right'. Defaults to 'right'.
        **kwargs: Additional keyword arguments to customize the float slider.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.float_slider.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/scale.html).
            
    Note: 
        You should never manually set the following arguments: *parent, label, from_, to, and command*.

    Returns:
        state: State of the widget. Can be used as a boolean to check if the value was modified.
        value: The current value selected on the slider.
    """
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
    """A slider widget for selecting integer values within a specified range.

    Example:
    ```python
    changed, current_value = imtk.int_slider(label="Adjust Value", val=current_value, vmin=0, vmax=100)
    if changed:
        print("The value changed to", current_value)
    ```

    Args:
        label (str): The label associated with the integer slider.
        val (int): The initial integer value displayed on the slider.

    Keyword Args:
        vmin (int, optional): The minimum allowed value. Defaults to 0.
        vmax (int, optional): The maximum allowed value. Defaults to 100.
        label_position (str, optional): The position of the label relative to the slider.
            Possible values: 'left', 'right'. Defaults to 'right'.
        **kwargs: Additional keyword arguments to customize the integer slider.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.int_slider.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/scale.html).
            
    Note: 
        You should never manually set the following arguments: *parent, label, from_, to, and command*.

    Returns:
        state: State of the widget. Can be used as a boolean to check if the value was modified.
        value: The current integer value selected on the slider.
    """
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
    """A combo box widget for selecting a value from a list of options.

    Example:
    ```python
    changed, current_index = imtk.combo_box(label="Select Option", current_index=selected_index, values=["Option 1", "Option 2"])
    if changed:
        print("The selected option changed to", values[current_index])
    ```

    Args:
        label (str): The label associated with the combo box.
        current_index (int): The initial index of the selected value in the combo box.
        values (Sequence[str]): The list of options displayed in the combo box.

    Keyword Args:
        label_position (str, optional): The position of the label relative to the combo box.
            Possible values: 'left', 'right'. Defaults to 'right'.
        **kwargs: Additional keyword arguments to customize the combo box.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.combo_box.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/optionmenu.html).
            
    Note: 
        You should never manually set the following arguments: *parent, label, variable, and command*.

    Returns:
        state: State of the widget. Can be used as a boolean to check if the selection was modified.
        index: The current index of the selected value in the combo box.
    """
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
) -> ImWidgetState:
    """A progress bar widget for visualizing the progress of a task.

    Example:
    ```python
    imtk.progress_bar(label="Loading", value=0.75, min_=0.0, max_=1.0, show_progress=True)
    ```

    Args:
        label (str): The label associated with the progress bar.
        value (float): The current value of the progress bar within the specified range.

    Keyword Args:
        min_ (float, optional): The minimum allowed value. Defaults to 0.0.
        max_ (float, optional): The maximum allowed value. Defaults to 1.0.
        label_position (str, optional): The position of the label relative to the progress bar.
            Possible values: 'left', 'right'. Defaults to 'right'.
        show_progress (bool, optional): Whether to display the current progress percentage next to the bar. Defaults to False.
        **kwargs: Additional keyword arguments to customize the progress bar.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to tk.progress_bar.
            See [Tkinter Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-Progressbar.html).
            
    Note: 
        You should never manually set the following arguments: *parent, value, mode, variable, and command*.

    Returns:
        ImWidgetState: State of the progress bar. Since this widget cannot be active, you will probably ignore this return value.
    """
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
def horizontal_separator(identifier:str, width:int=None, relwidth:float=0.95, **kwargs) -> ImWidgetState:
    """A horizontal separator widget.

    Example:
    ```python
    imtk.horizontal_separator("Separator 1", width=2, relwidth=0.8)
    ```

    Args:
        identifier (str): A unique identifier for the widget.
        width (int | None, optional): The width of the separator line in pixels. Defaults to None.
        relwidth (float, optional): The relative width of the separator as a fraction of the parent's width. Defaults to 0.95.

    Keyword Args:
        **kwargs: Additional keyword arguments to customize the separator widget.
            These arguments are defined by the concrete imtk backend implementation.
            Usually, this includes at least all arguments available to ttk.Separator.
            See [Tkinter TTK Reference](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-Separator.html).

    Note:
        You should never manually set the following arguments: *orient*.

    Returns:
        ImWidgetState: State of the widget.  Since this widget cannot be active, you will probably ignore this return value.
    """
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
