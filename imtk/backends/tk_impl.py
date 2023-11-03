import tkinter as tk
from typing import Tuple, Any, Callable, Dict

from ..base import ImContext


TK_WIDGET_FACTORIES = {
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


class TKFrame(tk.Frame, ImContext):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        ImContext.__init__(self)

    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return TK_WIDGET_FACTORIES
    

class TKWindow(tk.Tk, ImContext):
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
        background_color:str | None = '#ffffff'
    ):
        super().__init__()
        ImContext.__init__(self)

        self.title(title)
        
        if size:
            width, height = size
            self.geometry(f"{width}x{height}")
            
        
        if position is not None:
            xpos, ypos = position
            self.geometry(f"+{xpos}+{ypos}")
        
        if minsize is not None:
            width, height = minsize
            self.minsize(width, height)
        
        if maxsize is not None:
            width, height = maxsize
            self.maxsize(width, height)
        
        if isinstance(resizable, bool):
            resizable = (resizable, resizable)

        if resizable:
            width, height = resizable
            self.resizable(width, height)

        if scaling:
            try:
                self.tk.call("tk", "scaling", scaling)
            except:
                # TODO: Notify that this did not work
                pass

        # This should make sure _init is called after the
        # main loop was started using self.mainloop
        self._auto_resize = auto_resize or (not size)
        self._backround_color = background_color
        self.after_idle(self.on_init)

    
    def on_init(self):
        if self._backround_color:
            self._content_frame.config(background='#ffffff')
            self.configure(background='#ffffff')
        self.refresh()
        if self._auto_resize:
            self.configure(
                width=self._content_frame.winfo_reqwidth(),
                height=self._content_frame.winfo_reqheight(),
            )


    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        return TK_WIDGET_FACTORIES
    