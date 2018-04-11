from benwaonline.entities import Image, Preview
from .base import EntityGateway

class ImageGateway(EntityGateway):
    def __init__(self):
        super().__init__(Image)

class PreviewGateway(EntityGateway):
    def __init__(self):
        super().__init__(Preview)
