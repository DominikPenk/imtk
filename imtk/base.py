from __future__ import annotations

import abc
import tkinter as tk
from typing import Any, Callable, Dict, List, Optional, Tuple
from .cursor import ImCursor


class ImWidgetState(object):
    """
    Represents the state of an Immediate Mode GUI widget.

    This class stores information about a widget's state, including its widget object,
    position, custom data, and identifier.

    Args:
        widget (tk.Widget): The tkinter widget associated with this state.
        identifier (str): A unique identifier for the widget.
        position (Optional[Tuple[int, int]]): The position of the widget (x, y).
        new (bool): Indicates if the widget is newly created.
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
        self._active = False


    def __bool__(self) -> bool:
        return self._active


class ImNamespace:
    """Represents a namespace within an Immediate Mode GUI context.

    Namespaces are an easy way to avoid identifier conflicts.

    Args:
        context (ImContext): The parent frame to which this namespace belongs.
        name (str): The name of the namespace.
    """
    def __init__(self, context:'ImContext', name:str):
        self.context = context
        self.name = name

    def __enter__(self):
        self.context.namespace_push(self.name)

    def __exit__(self, *args):
        ns = self.context.namespace_pop()
        if ns != self.name:
            raise RuntimeError("Namespace stack corrupted")


class ImContext(abc.ABC):
    """
    Represents the main context for the Immediate Mode GUI.

    Args:
        refresh_mode (str): The mode for refreshing the GUI ('callback' or 'loop').
        loop_frequency (int): Frequency of the loop when using the 'loop' refresh mode.
    """
    __active__: ImContext | None = None

    def __init__(
        self, 
        refresh_mode:str='callback',
        loop_frequency:int=50
    ):
        # abc.ABC.__init__(self)
        super().__init__()
        self._widgets: Dict[str, ImWidgetState] = dict()
        self.active_widget:str | None = None
        self._cursor_stack: List[ImCursor] = []
        self._namespaces: List[str] = []
        self._widget_factories = self.install_widgets()
        self._refresh_mode = None
        self._after_id = None
        self.loop_frequency = loop_frequency

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
        # self._content_frame.propagate(0)

        # Ensure that the scroll bar is always in front of the content
        self.scrollbar.lift(self._content_frame)

   
        self.set_refresh_engine(refresh_mode, False)


    def __enter__(self) -> ImContext:
        if ImContext.__active__ is not None:
            raise RuntimeError("Tried to active a frame but there is already an active one")
        ImContext.__active__ = self


    def __exit__(self, *args):
        if ImContext.__active__ != self:
            raise RuntimeError("ImFrame __active__ corrupted")
        ImContext.__active__ = None
        

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
                    rely=0.0,
                    relheight=1.0,
                    anchor='ne'
                )
            first, _ = self.scrollbar.get()
            self.yview('moveto', str(first))


    def set_refresh_engine(self, method:str|int, loop_frequency:int|None=None):
        """
        Set the refresh engine mode and, if applicable, the loop frequency.

        This method allows you to configure the refresh engine mode for the context
        When using 'loop' mode, you may specify the frequency at which the GUI content will be refreshed.

        Args:
            method (str | int): The refresh mode to be used. Choose from:
                - 'callback': GUI content is refreshed on-demand when specific events trigger
                updates. Ideal for event-driven GUIs where updates occur in response to user actions.
                - 'loop': GUI content is refreshed at a specified frequency, creating a continuous
                and real-time rendering loop. Suitable for applications where the content changes
                without user interaction.
                - An integer: This is equivalent to passing 'loop' and a loop_frequency

            loop_frequency (int | None): The loop frequency, applicable only when 'loop' mode is selected.
                It represents the time interval (in milliseconds) between each refresh cycle. If method is
                'loop', loop_frequency is required. If method is an integer.

        Returns:
            None

        Example:
            To set the refresh engine to 'callback' mode and initiate refreshing:
            >>> set_refresh_engine('callback')

            To set the refresh engine to 'loop' mode with a refresh frequency of 60 milliseconds:
            >>> set_refresh_engine('loop', loop_frequency=60)

            To change the loop frequency without altering the refresh mode:
            >>> set_refresh_engine(30)  # Sets the loop frequency to 30 milliseconds
        """
        if isinstance(method, int):
            if loop_frequency is not None:
                raise ValueError("if method is an integer, loop_frequency must be None")
            self.loop_frequency = method
            self.method = 'loop'

        if method not in ['callback', 'loop']:
            raise ValueError("method must be 'callback' or 'loop'")
        self._refresh_mode = method
        if self._after_id:
            self.after_cancel(self._after_id)
        
        if method == 'loop' and loop_frequency is not None:
            self.loop_frequency = loop_frequency 
        self.refresh()


    def init_cursor(self) -> ImCursor:
        return ImCursor()


    def yview(self, *args):
        """
        Scroll the GUI content vertically.

        This method is responsible for vertical scrolling of the Immediate Mode GUI content.
        It adjusts the scrollbar position and the content frame's relative placement to
        achieve the desired scrolling effect. The method is typically invoked in response to
        user interactions with the scrollbar or mouse wheel.
        """
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
        """
        Refresh the Immediate Mode GUI content.

        This method is the core of the ImTk, ensuring that the GUI content is up to date, 
        correctly drawn, and responsive to user interactions. 
        It also manages the refresh mode and cursor stack to maintain GUI consistency.

        Note:
        - When using the 'loop' refresh mode, the refresh cycle is scheduled at a specified
        frequency to provide real-time updates and interactivity.

        - This method should not be called directly by users; it is automatically called by
        the framework to manage GUI rendering and updates.
        """
        # Prevent interlaced refesh calles due to parallelism
        # Maybe use a lock instead?
        if ImContext.__active__:
            return

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
        
        # remove not drawn widgets
        widgets_to_remove = [
            key for key, info in self._widgets.items() if not info.drawn
        ]
        for key in widgets_to_remove:
            info = self._widgets.pop(key)
            info.widget.destroy()

        content_width, content_height = base_cursor.size
        self._content_frame.configure(
            width=content_width,
            height=content_height
        )

        self._hide_or_display_scrollbar()

        # Reset the information from this refresh call
        for info in self._widgets.values():
            info.drawn = False

        should_recurse = self.active_widget is not None and self._refresh_mode == 'callback'
        self.active_widget = None

        if should_recurse:
            # We need to call this recursively if something
            # before the active object changed based on its activation
            self.refresh()
        elif self._refresh_mode == 'loop':
            self._after_id = self.after(self.loop_frequency, self.refresh)
            # self._after_id = self.after_idle(self.refresh)


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
        """
        Get a namespaced identifier for a value within the current context.

        Args:
            val (str): The value to be namespaced.

        Returns:
            str: The namespaced identifier.

        Note:
            The format of the namespaced identifier includes the current namespace's name,
            followed by a double colon (::), and the provided value. This format helps
            ensure unique and context-specific identifiers.
        """
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
        """
        Get the current content frame for GUI drawing.

        Returns:
            tk.Widget: The content frame for drawing.
        """
        return self.cursor.get_frame_widget() or self._content_frame


    def create_widget(
        self, 
        type:str, 
        *, 
        master:tk.Widget=None, 
        **kwargs
    ) -> tk.Widget:
        """
        Create a new GUI widget of the specified type. You probably will never call this
        method yourself it is internally called by the immediate GUI functions.

        Args:
            type (str): The type of the widget to create.
            master (tk.Widget): The parent widget to contain the new widget. (Default is None.)
            **kwargs: Additional keyword arguments for widget configuration.

        Returns:
            tk.Widget: The newly created widget.
        """
        if type not in self._widget_factories:
            msg = f"Widget '{type}' was not installed with your backend implementation" \
                   "check out the 'install_widgets' method."
            raise RuntimeError(msg)
        master = master or self.get_current_content_frame()
        return self._widget_factories[type](master=master, **kwargs)


    @abc.abstractmethod
    def draw(self) -> None:
        """
        Abstract method for drawing the GUI content.

        This method must be implemented in subclasses to define the GUI layout and elements.
        """
        pass
    

    @abc.abstractmethod
    def install_widgets(self) -> Dict[str, Callable[[Any], tk.Widget]]:
        """In this function you must populate
        self._tk_widgets dict
        """
        pass


    @property
    def current_namespace(self) -> str:
        """
        Get the current namespace.

        Returns:
            str: The name of the current namespace.
        """
        return self._namespaces[-1] if self._namespaces else ""


    @property
    def cursor(self) -> ImCursor:
        """
        Get the current cursor for managing GUI drawing.

        Returns:
            ImCursor: The current cursor.
        """
        if not self._cursor_stack:
            raise RuntimeError("No active cursor found")
        return self._cursor_stack[-1]


def get_context() -> ImContext:
    """
    Get the currently active Immediate Mode GUI context.

    Returns:
        ImContext: The active GUI context.
    """
    if ImContext.__active__ is None:
        raise RuntimeError("No active context")
    return ImContext.__active__


def namespace(name:str, context:Optional[ImContext]=None) -> ImNamespace:
    """
    Create namespace within an Immediate Mode GUI context.

    Namespaces are a mechanism for organizing and isolating identifiers and widgets within an
    Immediate Mode GUI context. They help prevent naming conflicts.

    Args:
        name (str): The name of the namespace to create..

        context (ImContext | None): The Immediate Mode GUI context in which the namespace should be
            created. If provided, the namespace is associated with the specified context. If not
            provided, the function uses the active context. (Default is None.)

    Returns:
        ImNamespace: An ImNamespace instance representing the created namespace.

    Example:
        # Create a namespace within the active context using a 'with' statement
        with namespace("my_namespace"):
            # Within this block, all widget identifiers and actions are scoped to 'my_namespace'
            if imtk.button("A button"):
                print("The button was clicked")
    """
    context = context or get_context()
    return context.namespace(name)


def get_identifier(val:str, context:Optional[ImContext]=None) -> str:
    """
    Get a namespaced identifier for a value within a specific context.

    Args:
        val (str): The value to be namespaced.
        context (Optional[ImContext]): The context in which to get the identifier.
            If not provided, the function uses the currently active context, if available.

    Returns:
        str: The namespaced identifier.
    """
    context = context or get_context()
    return context.get_identifier(val)
