from benwaonline.schemas import TagSchema
from .base import Entity

class Tag(Entity):
    '''Represents a Tag resource object, related to the Tag model in the database

    Attributes:
        type_: 'Tag'

    '''
    schema = TagSchema
    type_ = schema.Meta.type_
    attrs = {}

    def __init__(self, id=None, name=None, created_on=None, posts=None, num_posts=0):
        self.id = id
        self.name = name
        self.created_on = created_on
        self.posts = posts or []
        self.num_posts = num_posts

    def __repr__(self):
        return '<Tag {} - {}>'.format(self.id, self.name)
