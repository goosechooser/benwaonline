from benwaonline.schemas import CommentSchema
from .base import Entity

class Comment(Entity):
    '''Represents a Comment resource object, related to the Comment model in the database

    Attributes:
        type_: 'comments'

    '''
    schema = CommentSchema
    type_ = schema.Meta.type_
    attrs = {
        'posts': 'post',
        'users': 'user'
    }

    def __init__(self, id=None, content=None, created_on=None, user=None, post=None, poster=None, metadata=None):
        self.id = id
        self.content = content
        self.created_on = created_on
        self.user = user
        self.post = post
        self.poster = poster
        self.metadata = metadata
