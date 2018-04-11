from benwaonline.schemas import ImageSchema, PreviewSchema
from .base import Entity

class Image(Entity):
    '''Represents a Image resource object, related to the Image model in the database

    Attributes:
        type_: 'images'

    '''
    schema = ImageSchema
    type_ = schema.Meta.type_
    attrs = {}

    def __init__(self, id=None, filepath=None, created_on=None):
        self.id = id
        self.filepath = filepath
        self.created_on = created_on

class Preview(Image):
    '''Represents a Preview resource object, related to the Preview model in the database

    Attributes:
        type_: 'previews'

    '''
    schema = PreviewSchema
    type_ = schema.Meta.type_
    attrs = {}
