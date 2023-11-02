from __future__ import annotations

import abc
import tkinter as tk
from typing import Any, Callable, Dict, List, Optional, Tuple
from .cursor import ImCursor


class ImWidgetState(object):
    """Represents the state of an Immediate Mode GUI widget.

    This class stores information about a widget's state, including its widget object,
    position, custom data, and identifier.

    Args:
        widget (tk.Widget): The tkinter widget associated with this state.
        identifier (str): A unique identifier for the widget.
        position (Optional[Tuple[int, int]]): The position of the widget (x, y).
        new (bool): Indicates if the widget is new.
        drawn (bool): Indicates if the widget has been drawn.
        custom_data (Optional[Dict[str, Any]]): Custom data associated with the widget.
    """
    def __init__(
        self,
        widget:tk.Widget,
        identifier:str,
        position:Optional[Tuple[int, int]]=None,
        new:bool=True,
        drawn:bool=True,
        custom_data:Optional[Dict[str, Any]] = None
    ) -> None:
        self.widget = widget
        self.position = position
        self.new = new
        self.drawn = drawn
        self.custom_data = custom_data or dict()
        self.identifier = identifier


class ImNamespace:
    """Represents a namespace within an Immediate Mode GUI frame.

    Namespaces are an easy way to avoid identifier conflicts.

    Args:
        context (ImFrame): The parent frame to which this namespace belongs.
        name (str): The name of the namespace.
    """
    def __init__(self, context:'ImFrame', name:str):
        self.context = context
        self.name = name

    def __enter__(self):
        self.context.namespace_push(self.name)

    def __exit__(self, *args):
        ns = self.context.namespace_pop()
        if ns != self.name:
            raise RuntimeError("Namespace stack corrupted")


class ImFrame(tk.Frame, abc.ABC):
    __active__ = []

    def __init__(
        self, 
        master=None, 
        refresh_mode:str='callback'
    ):
        tk.Frame.__init__(self, master=master, relief='flat')
        abc.ABC.__init__(self)
        self._widgets: Dict[str, ImWidgetState] = dict()
        self.active_widget:str | None = None
        self._command_buffer: List[Callable[[], None]] = list()
        self._cursor_stack: List[ImCursor] = []
        self._namespaces: List[str] = []
        self._widget_factories = self.install_widgets()
        self._refresh_mode = None
        self._after_id = None

        # Get the scrollbar
        self.scrollbar = self.create_widget(
            "scrollbar", 
            master=self, 
            orient="vertical",
            command=self.yview    
        )
        self.bind("<Configure>", self._hide_or_display_scrollbar)

        # widget event binding
        self.winsys = self.tk.call("tk", "windowingsystem")
        self.bind("<Enter>", self._add_scroll_binding, "+")
        self.bind("<Leave>", self._del_scroll_binding, "+")

        self._content_frame = tk.Frame(self)
        self._content_frame.propagate(0)
        self._content_frame.pack(side='top', anchor='w')
   
        self.set_refresh_engine(refresh_mode, False)


    def __enter__(self) -> ImFrame:
        ImFrame.__active__.append(self)


    def __exit__(self, *args):
        active = ImFrame.__active__.pop()
        if active != self:
            raise RuntimeError("ImFrame stack corrupted")
        

    def _get_scroll_measure(self):
        outer = self.winfo_height()
        inner = max(self._content_frame.winfo_reqheight(), outer)

        base = inner / outer
        if inner == outer:
            thumb = 1.0
        else:
            thumb = outer / inner
        return base, thumb


    def _add_scroll_binding(self, *args, parent:tk.Widget|None=None):
        parent = parent or self._content_frame
        children = parent.winfo_children()
        for widget in [parent, *children]:
            bindings = widget.bind()
            if self.winsys.lower() == "x11":
                if "<Button-4>" in bindings or "<Button-5>" in bindings:
                    continue
                else:
                    widget.bind("<Button-4>", self._on_mousewheel, "+")
                    widget.bind("<Button-5>", self._on_mousewheel, "+")
            else:
                if "<MouseWheel>" not in bindings:
                    widget.bind("<MouseWheel>", self._on_mousewheel, "+")
            if widget.winfo_children() and widget != parent:
                self._add_scroll_binding(parent=widget)


    def _del_scroll_binding(self, *args, parent:tk.Widget|None=None):
        parent = parent or self._content_frame
        """Recursive removal of scrolling binding for all descendants"""
        children = parent.winfo_children()
        for widget in [parent, *children]:
            if self.winsys.lower() == "x11":
                widget.unbind("<Button-4>")
                widget.unbind("<Button-5>")
            else:
                widget.unbind("<MouseWheel>")
            if widget.winfo_children() and widget != parent:
                self._del_scroll_binding(parent=widget)


    def _on_mousewheel(self, event):
        """Callback for when the mouse wheel is scrolled."""
        if self.winsys.lower() == "win32":
            delta = -int(event.delta / 100)
        elif self.winsys.lower() == "aqua":
            delta = -event.delta
        elif event.num == 4:
            delta = -10
        elif event.num == 5:
            delta = 10
        
        first, _ = self.scrollbar.get()
        fraction = delta / 100 + first
        self.yview('moveto', str(fraction))


    def _hide_or_display_scrollbar(self, *args):
        content_height = self._content_frame.winfo_reqheight()
        frame_height   = self.winfo_height()

        if frame_height >= content_height and self.scrollbar.winfo_ismapped():
            self.scrollbar.place_forget()
            self._content_frame.place(rely=0)
        elif frame_height < content_height:
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.place(
                    relx=1.0, 
                    x=-self.scrollbar.winfo_reqwidth(),
                    relheight=1.0
                )
            first, _ = self.scrollbar.get()
            self.yview('moveto', str(first))


    def set_refresh_engine(self, method:str, do_refresh:bool=True):
        if method not in ['callback', 'loop']:
            raise ValueError("method must be 'callback' or 'loop'")
        self._refresh_mode = method
        if self._after_id:
            self.after_cancel(self._after_id)
        if do_refresh:
            self.refresh()


    def init_cursor(self) -> ImCursor:
        return ImCursor()


    def yview(self, *args):
        if args[0] == "moveto":
            base, thumb = self._get_scroll_measure()
            fraction = float(args[1])
            if fraction < 0:
                first = 0.0 
            elif (fraction + thumb) > 1:
                first = 1 - thumb
            else:
                first = fraction
            self.scrollbar.set(first, first+thumb)
            self._content_frame.place(rely=-first*base)


    def refresh(self) -> None:
        if self._cursor_stack:
            raise RuntimeError("The cursor stack is corrupted, it should be empty")
        
        base_cursor = self.push_cursor()
        with self:
            self.draw()

        self.pop_cursor()
        if self._cursor_stack:
            msg = f"The cursor stack is corrupted, " \
                  f"it should be empty, " \
                  f"but has size {len(self._cursor_stack)}" 
            raise RuntimeError(msg)
        
        content_width, content_height = base_cursor.size
        self._content_frame.configure(
            width=content_width,
            height=content_height
        )

        self._hide_or_display_scrollbar()


        for cmd in self._command_buffer:
            cmd()

        # remove not drawn widgets
        widgets_to_remove = [
            key for key, info in self._widgets.items() if not info.drawn
        ]
        for key in widgets_to_remove:
            info = self._widgets.pop(key)
            info.widget.destroy()

        # Reset the information from this refresh call
        self._command_buffer.clear()
        for info in self._widgets.values():
            info.drawn = False

        should_recurse = self.active_widget is not None and self._refresh_mode == 'callback'
        self.active_widget = None

        if should_recurse:
            # We need to call this recursively if something
            # before the active object changed based on its activation
            print("Recursive Refresh")
            self.refresh()
        elif self._refresh_mode == 'loop':
            self.update_idletasks()
            self._after_id = self.after_idle(self.refresh)


    def set_active(self, identifier:str):
        self.active_widget = identifier
        if self._refresh_mode == 'callback':
            self.refresh()


    def namespace_push(self, name:str):
        self._namespaces.append(name)


    def namespace_pop(self) -> str:
        return self._namespaces.pop()


    def namespace(self, name:str) -> ImNamespace:
        return ImNamespace(self, name)


    def get_identifier(self, val:str):
        return f"{self.current_namespace}::{val}" if self.current_namespace else val


    def push_cursor(self, cursor:ImCursor | None = None) -> ImCursor:
        parent = self._cursor_stack[-1] if self._cursor_stack else None
        cursor = cursor or self.init_cursor()
        cursor.parent = parent
        self._cursor_stack.append(cursor)
        return cursor
    
    
    def pop_cursor(self) -> ImCursor:
        if not self._cursor_stack:
            raise RuntimeError("The cursor stack was corrupted. No active cursor")
        return self._cursor_stack.pop()


    def get_current_content_frame(self):
        return self.cursor.get_frame_widget() or self._content_frame


    def create_widget(
        self, 
        type:str, 
        *, 
        master:tk.Widget=None, 
        **kwargs
    ) -> tk.Widget:
        if type not in self._widget_factories:
            msg = f"Widget '{type}' was not installed with your backend implementation" \
                   "check out the 'install_widgets' method."
            raise RuntimeError(msg)
        master = master or self.get_current_content_frame()
        return self._widget_factories[type](master=master, **kwargs)


    @abc.abstractmethod
    def draw(self) -> None:
        pass
    

    @abc.abstractmethod
    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        """In this function you must populate
        self._tk_widgets dict
        """
        pass


    @property
    def current_namespace(self) -> str:
        return self._namespaces[-1] if self._namespaces else ""


    @property
    def cursor(self) -> ImCursor:
        if not self._cursor_stack:
            raise RuntimeError("No active cursor found")
        return self._cursor_stack[-1]


def get_context() -> ImFrame:
    if len(ImFrame.__active__) == 0:
        raise RuntimeError("No active context")
    return ImFrame.__active__[-1]


def namespace(name:str, context:Optional[ImFrame]=None) -> ImNamespace:
    context = context or get_context()
    return context.namespace(name)


def get_identifier(val:str, context:Optional[ImFrame]=None) -> str:
    context = context or get_context()
    return context.get_identifier(val)
