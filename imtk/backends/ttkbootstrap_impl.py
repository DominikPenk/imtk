import tkinter as tk
from typing import Any, Callable, Dict

import ttkbootstrap

from ..base import ImContext

TTKBOOTSTRA_WIDGET_FACTORIES = {
    'button': ttkbootstrap.Button,
    'checkbutton': ttkbootstrap.Checkbutton,
    'combobox': ttkbootstrap.Combobox,
    'entry': ttkbootstrap.Entry,
    'label': ttkbootstrap.Label,
    'scale': ttkbootstrap.Scale,
    'spinbox': ttkbootstrap.Spinbox,
    'progressbar': ttkbootstrap.Progressbar,
    'separator': ttkbootstrap.Separator,
    'scrollbar': ttkbootstrap.Scrollbar,
    'labelframe': ttkbootstrap.LabelFrame,
    'frame': ttkbootstrap.Frame
}

class TTKBootstrapFrame(ttkbootstrap.Frame, ImContext):
    def __init__(self, master=None, **kwargs):
        ttkbootstrap.Frame.__init__(self, master, **kwargs)
        ImContext.__init__(self)

    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return TTKBOOTSTRA_WIDGET_FACTORIES
    

class TTKBootstrapWindow(ttkbootstrap.Window, ImContext):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ImContext.__init__(self)

        self.after_idle(self.refresh)

    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return TTKBOOTSTRA_WIDGET_FACTORIES
