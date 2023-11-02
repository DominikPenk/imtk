import tkinter as tk
from typing import Any, Callable, Dict

import tkinter.ttk as ttk

from ..base import ImFrame


class TTKFrame(ttk.Frame, ImFrame):
    def __init__(self, master=None, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        ImFrame.__init__(self)

    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return {
            'button': ttk.Button,
            'checkbutton': ttk.Checkbutton,
            'combobox': ttk.Combobox,
            'entry': ttk.Entry,
            'label': ttk.Label,
            'scale': ttk.Scale,
            'spinbox': ttk.Spinbox,
            'progressbar': ttk.Progressbar,
            'scrollbar': ttk.Scrollbar,
            'labelframe': ttk.LabelFrame,
            'frame': ttk.Frame
        }