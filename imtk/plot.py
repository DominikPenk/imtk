import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.artist import Artist
import tkinter as tk
from typing import Callable
from tkinter import Pack, Place, Grid


from . import base
from .functional import imtk_widget, _strip_label

__all__ = [
    'Plot',
    'plot'
]

class Plot(object):
    def __init__(
        self, 
        height:int=480, 
        width:int=640,
        dpi:int=96
    ) -> None:
        self.height = height
        self.width = width
        self.dpi = dpi
        self.figure = plt.figure(
            figsize=(self.width/self.dpi, self.height/self.dpi),
            dpi=self.dpi
        )
        self._tk_canvas = None


    def __enter__(self):
        plt.figure(self.figure.number)


    def __exit__(self, *args):
        if self._tk_canvas and not self.stale:
            self._tk_canvas.draw()

        
    def create_widget(self, master:tk.Widget | None = None) -> tk.Widget:
        if self._tk_canvas:
            raise RuntimeError("This Plot is already associated with a tk widget.")
        self._tk_canvas = FigureCanvasTkAgg(self.figure, master)
        return self._tk_canvas.get_tk_widget()


    def set_draw_callback(self, callback:Callable[[None], None]):
        self._on_draw = callback

    
    def draw(self):
        if not self._tk_canvas:
            raise RuntimeError("Canvas was not yet created")
        self._tk_canvas.draw()


    @property
    def stale(self) -> bool:
        self.figure.stale


    @stale.setter
    def stale(self, val:bool):
        self.figure.stale = val


    @property
    def title(self) -> str:
        self.figure.get_suptitle()


    @title.setter
    def title(self, title:str) -> None:
        if self.figure.get_suptitle() != title:
            self.figure.suptitle(title)
            self.stale = False


@imtk_widget()
def plot(
    label:str,
    plot:Plot,
    identifier:str|None = None
) -> base.ImWidgetState:
    context = base.get_context()
    idx = context.get_identifier(identifier or label)
    info = context._widgets.get(idx, None)
    if info is None:
        info = base.ImWidgetState(
            widget=plot.create_widget(context.get_current_content_frame()),
            identifier=idx
        )


    plot.title = _strip_label(label)
    if not plot.stale:
        plot.draw()
    
    return info
        