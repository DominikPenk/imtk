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
    """Create an Immediate Mode GUI widget for displaying an image.

    Example:
    ```python
    # Assuming 'my_image' is a PIL Image or another compatible image type
    imtk.image(identifier="image_widget_1", image=my_image, size=(200, 150))
    ```
    
    Args:
        identifier (str): A unique identifier for the widget.
        image (ImageLike): The image to be displayed. Must be compatible with the backend.
        size (Tuple[int, int] | None, optional): The size of the displayed image. Defaults to None.
        **kwargs: Additional keyword arguments for customizing the image widget.

    Returns:
        base.ImWidgetState: The state of the widget. Since this widget cannot be active, you will probably ignore this return value.


    Note:
        - The *ImageLike* type represents an image object compatible with the backend (PIL Image or NumPy array).
        - Additional keyword arguments are backend-specific and may include parameters for
          image positioning, scaling, or other customizations.

    """
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