from benwaonline.schemas import LikeSchema
from .base import Entity

class Like(Entity):
    schema = LikeSchema
    type_ = schema.Meta.type_

    def __init__(self, id=None):
        self.id = id

    def __repr__(self):
        return '<Like {}>'.format(self.id)
