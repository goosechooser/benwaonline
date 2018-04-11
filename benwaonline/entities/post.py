from .base import Entity
from benwaonline.schemas import PostSchema

class Post(Entity):
    '''Represents a Post resource object, related to the Post model in the database

    Attributes:
        type_: 'posts'

    '''
    schema = PostSchema
    type_ = schema.Meta.type_
    relationships = ['user', 'comments', 'image', 'preview', 'tags', 'likes']
    attrs = {
        'previews': 'preview',
        'images': 'image',
        'users': 'user'
    }

    def __init__(self, id=None, title=None, created_on=None, user=None, comments=None, image=None, preview=None, tags=None, likes=None):
        self.id = id
        self.title = title
        self.created_on = created_on
        self.user = user
        self.comments = comments or []
        self.image = image
        self.preview = preview
        self.tags = tags or []
        self.likes = likes or []

    def __repr__(self):
        return '<Post {}: {}>'.format(self.id, self.title)

class PostLike(Post):
    type_ = 'likes'
