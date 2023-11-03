from __future__ import annotations

import copy
import tkinter as tk
from typing import TYPE_CHECKING, Optional, Tuple

from . import base

if TYPE_CHECKING:
    from .base import ImContext, ImWidgetState


class SameRowContext:
    def __init__(self, cursor:ImCursor):
        self.cursor = cursor
        self.stay_in_row = cursor.stay_in_row

    # This is a "hack" to ensure that the first
    # time a widget is added we return the value
    # originally stored in cursor.stay_in_row 
    # afterwards we always return True
    def __bool__(self):
        r = self.stay_in_row
        self.stay_in_row = True
        return r
    
    def __enter__(self):
        self.cursor.stay_in_row = self

    def __exit__(self, *args):
        self.cursor.stay_in_row = False


class ImCursor(object):
    def __init__(self, parent:'ImCursor' | None = None):
        self.stay_in_row: bool | SameRowContext = False
        self.padding    = 5
        self.position   = [self.padding, self.padding]
        self.row_height = 0
        self.col_width  = 0
        self.frame: base.ImWidgetState | None = None
        self.parent = parent
        # For some reason we need to add a little bit of height for labelframe
        # TODO: find out why and fix it
        self._frame_end_padding: int = 0  


    def __enter__(self):
        pass

    def __exit__(self, *args):
        context = base.get_context()
        top_cursor = context.pop_cursor()
        if top_cursor != self:
            raise RuntimeError("The cursor context is corrupted")
        
        if self.parent and self.frame:
            if context.cursor != self.parent:
                raise RuntimeError("The cursor stack is corrupted. "
                                   "The active cursor is not the parent")

            w, h = self.size            
            self.frame.widget.configure(width=w, height=h+self._frame_end_padding)
            self.parent.add_widget(self.frame, context)
        

    def move(self, dx:float|None, dy:float|None):
        if dx is not None:
            self.position[0] += dx
        if dy is not None:
            self.position[1] += dy


    def add_widget(
        self, 
        info:ImWidgetState,
        context:Optional[ImContext]=None,
        **kwargs
    ) -> None:
        context = context or base.get_context()

        if not self.stay_in_row:
            self.position[0] = self.padding
            self.position[1] += self.row_height + self.padding
            self.row_height = 0
        else:
            self.position[0] += self.padding
            if not isinstance(self.stay_in_row, SameRowContext):  #TODO: Can we hide this in SameRowContext?
                self.stay_in_row = False

        if info.new:
            context._widgets[info.identifier] = info
            info.new = False


        if info.position != self.position:
            info.position = copy.copy(self.position)
            info.widget.place(x=info.position[0], y=info.position[1], **kwargs)

        self.row_height = max(self.row_height, info.widget.winfo_reqheight())

        self.position[0] += info.widget.winfo_reqwidth()
        self.col_width = max(self.col_width, self.position[0])

        info.drawn = True


    def get_frame_widget(self) -> tk.Widget | None:
        if self.frame is None:
            return None
        else:
            return self.frame.widget

    def same_row(self) -> None:
        self.stay_in_row = True


    def row(self) -> SameRowContext:
        return SameRowContext(self)


    @property
    def size(self) -> Tuple[int, int]:
        return self.col_width + self.padding, self.position[1] + self.row_height + self.padding

