from typing import TypeAlias, Tuple
import numpy as np
from PIL import Image, ImageTk


from . import base

ImageLike: TypeAlias = Image.Image | np.ndarray

__all__ = ['image']

# TODO: I would like to call _convert_to_tkimage only if the image was updated
# Ideas:
#   - Proxy class for images?

def _convert_to_tkimage(
    img: ImageLike, 
    size:Tuple[int, int] | None = None
) -> ImageTk.PhotoImage:
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    
    if not isinstance(img, Image.Image):
        ValueError("image must be a PIL image or numpy array")

    if size:
        img = img.resize(size)

    return ImageTk.PhotoImage(img)

def image(
    identifier:str, 
    image:ImageLike,
    size:Tuple[int, int] | None = None,
    **kwargs
) -> base.ImWidgetState:
    context = base.get_context()

    idx = context.get_identifier(identifier)
    info = context._widgets.get(idx, None)
    if info is None:
        data = {
            'image': _convert_to_tkimage(image, size)
        }
        info = base.ImWidgetState(
            widget=context.create_widget(
                "label",
                image=data['image'],
                **kwargs
            ),
            identifier=idx,
            custom_data=data
        ) 
    else:
        info.custom_data['image'] = _convert_to_tkimage(image)
        info.widget.configure(image=info.custom_data['image'])
    
    context.cursor.add_widget(info)