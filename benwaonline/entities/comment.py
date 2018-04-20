from benwaonline.schemas import CommentSchema
from benwaonline.entities import Entity

class Comment(Entity):
    '''Represents a Comment resource object, related to the Comment model in the database

    Attributes:
        type_: 'comments'

    '''
    _schema = 'CommentSchema'
    type_ = 'comment'
    attrs = {}

    def __init__(self, id=None, content=None, created_on=None, user=None, post=None, poster=None, metadata=None):
        self.content = content
        self.created_on = created_on
        self.user = user
        self.post = post
        self.poster = poster
        self.metadata = metadata
        super().__init__(id=id)


    def __repr__(self):
        return '<Comment {}>'.format(self.id)
