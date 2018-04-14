from benwaonline.schemas import ImageSchema, PreviewSchema
from benwaonline.entities import Entity

class Image(Entity):
    '''Represents a Image resource object, related to the Image model in the database

    Attributes:
        type_: 'images'

    '''
    _schema = 'ImageSchema'
    type_ = 'image'
    attrs = {}

    def __init__(self, id=None, filepath=None, created_on=None):
        self.filepath = filepath
        self.created_on = created_on
        super().__init__(id=id)

    def __repr__(self):
        return '<Image {}>'.format(self.id)



    def __repr__(self):
        return '<Preview {}>'.format(self.id)