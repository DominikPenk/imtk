import tkinter as tk
from typing import Any, Callable, Dict

import ttkbootstrap

from ..base import ImFrame


class TTKBootstrapFrame(ttkbootstrap.Frame, ImFrame):
    def __init__(self, master=None, **kwargs):
        ttkbootstrap.Frame.__init__(self, master, **kwargs)
        ImFrame.__init__(self)

    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return {
            'button': ttkbootstrap.Button,
            'checkbutton': ttkbootstrap.Checkbutton,
            'combobox': ttkbootstrap.Combobox,
            'entry': ttkbootstrap.Entry,
            'label': ttkbootstrap.Label,
            'scale': ttkbootstrap.Scale,
            'spinbox': ttkbootstrap.Spinbox,
            'progressbar': ttkbootstrap.Progressbar,
            'separator': ttkbootstrap.Separator,
            'scrollbar': ttkbootstrap.Scrollbar
        }