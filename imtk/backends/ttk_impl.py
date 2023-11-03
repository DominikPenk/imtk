import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Callable, Dict, Tuple

from ..base import ImContext
from .tk_impl import TKWindow

TTK_WIDGET_FACTORIES = {
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


class TTKFrame(ttk.Frame, ImContext):
    def __init__(self, master=None, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        ImContext.__init__(self)

    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return TTK_WIDGET_FACTORIES
    
    
class TTKWindow(TKWindow):
    def __init__(
        self,
        title:str="ImTK Window",
        auto_resize:bool | None = None,
        size:Tuple[int, int] | None = None,
        position:Tuple[int, int] | None = None,
        minsize:Tuple[int, int] | None = None,
        maxsize:Tuple[int, int] | None = None,
        resizable:Tuple[bool, bool] | bool | None = None,
        scaling:float | None = None,
    ) -> None:
        super().__init__(title, auto_resize, size, position, minsize, maxsize, resizable, scaling)


    def on_init(self):
        self.style = ttk.Style()
        super().on_init()


    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return TTK_WIDGET_FACTORIES
    
    