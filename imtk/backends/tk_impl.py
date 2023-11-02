import tkinter as tk
from typing import Any, Callable, Dict

from ..base import ImFrame


class TKFrame(tk.Frame, ImFrame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        ImFrame.__init__(self)

    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return {
            'button': tk.Button,
            'checkbutton': tk.Checkbutton,
            'entry': tk.Entry,
            'label': tk.Label,
            'scale': tk.Scale,
            'spinbox': tk.Spinbox,
            'scrollbar': tk.Scrollbar,
            'labelframe': tk.LabelFrame,
            'frame': tk.Frame
        }