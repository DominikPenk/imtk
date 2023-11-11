In this module you will find functions to add elements to your immediate GUI.
All methods return a ImWidgetState for internal reasons. 
Also the state contains some internal information you should usually treat it as an indicator if the element is active, like this:
 
```python
cur_val = "Hello, World!"

if imtk.button("Button"):
    print("An 'active' button means it was clicked")

active, cur_val = imtk.input_text(label="Text input", text_=cur_val)
if active:
    print("An 'active' input implies that the value changed")
```

As you can see some UI elements might return multiple values. 
In these cases, the first one is always the ImWidgetState and the following are the (updated) versions of the input (e.g. the value of a text input)

::: imtk.functional
    options:
        members:
            - button
            - checkbox
            - combo_box
            - horizontal_separator
::: imtk
    options:
        members:
            - image

## Input Fields

::: imtk.functional
    options:
        members:
            - input_text
            - input_int
            - input_float
        heading_level: 3


::: imtk.functional
    options:
        members:
            - progress_bar


## Sliders

::: imtk.functional
    options:
        members:
            - int_slider
            - float_slider
        heading_level: 3



