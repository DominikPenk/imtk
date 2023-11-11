import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from typing import Callable


from . import base
from .functional import imtk_widget, _strip_label

__all__ = [
    'Plot',
    'plot'
]

class Plot(object):
    """A wrapper for Matplotlib plots integrated with Tkinter.

    This class provides a convenient interface for creating Matplotlib plots
    that can be embedded within Tkinter applications.

    Args:
        height (int, optional): The height of the plot in pixels. Defaults to 480.
        width (int, optional): The width of the plot in pixels. Defaults to 640.
        dpi (int, optional): Dots per inch for the plot. Defaults to 96.

    Example:
    ```python
    with Plot() as plot:
        plt.plot([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])
        plot.create_widget(master=tk.Tk())
    ```

    Note:
        The plot can be used as a context manager, ensuring that the Matplotlib figure
        is the currently active figure during the block.

    Attributes:
        height (int): The height of the plot.
        width (int): The width of the plot.
        dpi (int): Dots per inch for the plot.
        figure (matplotlib.figure.Figure): The Matplotlib figure.
        _tk_canvas (FigureCanvasTkAgg): The Tkinter canvas for embedding the plot.
    """
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
        """Set a callback function to be called on each draw.

        Args:
            callback (Callable[[None], None]): The callback function.
        """
        self._on_draw = callback

    
    def draw(self):
        if not self._tk_canvas:
            raise RuntimeError("Canvas was not yet created")
        self._tk_canvas.draw()


    @property
    def stale(self) -> bool:
        """Flag indicating if the Matplotlib figure is stale.

        Returns:
            bool: True if the figure is stale, False otherwise.
        """
        self.figure.stale


    @stale.setter
    def stale(self, val:bool):
        self.figure.stale = val


    @property
    def title(self) -> str:
        """Get the title of the Matplotlib figure.

        Returns:
            str: The title of the figure.
        """
        self.figure.get_suptitle()


    @title.setter
    def title(self, title:str) -> None:
        """Set the title of the Matplotlib figure.

        Args:
            title (str): The new title for the figure.
        """
        if self.figure.get_suptitle() != title:
            self.figure.suptitle(title)
            self.stale = False


@imtk_widget()
def plot(
    label:str,
    plot:Plot,
    identifier:str|None = None
) -> base.ImWidgetState:
    """Create an Immediate Mode GUI widget for embedding a Matplotlib plot.

    Args:
        label (str): The label associated with the plot.
        plot (Plot): The Plot instance containing the Matplotlib plot.
        identifier (str | None, optional): An optional identifier for the widget. Defaults to None.

    Returns:
        base.ImWidgetState: The state of the widget. Since a plot widget is never active you will probably ignore this value.

    Example:
    ```python
    # Create a Matplotlib plot
    my_plot = Plot(figsize=(3, 2), dpi=100)
    # Create an Immediate Mode GUI widget for the Matplotlib plot
    my_plot = imtk.plot(label="My Custom Plot", plot=my_plot)
    
    ...

    with my_plot:
        plt.plot([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])
    ```
    """
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
        