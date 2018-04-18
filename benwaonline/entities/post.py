from benwaonline.entities import Entity
from benwaonline.gateways import PostGateway

class Post(Entity):
    '''Represents a Post resource object, related to the Post model in the database

    Attributes:
        type_: 'post'

    '''
    _schema = 'PostSchema'
    type_ = 'post'
    attrs = {
        'comment': 'comments',
        'tag': 'tags',
        'like': 'likes'
    }

    def __init__(self, id=None, title=None, created_on=None, user=None, comments=None, image=None, preview=None, tags=None, likes=None):
        self.title = title
        self.created_on = created_on
        self.user = user
        self.comments = comments or []
        self.image = image
        self.preview = preview
        self.tags = tags or []
        self.likes = likes or []
        super().__init__(id=id)

    def __repr__(self):
        return '<Post {}: {}>'.format(self.id, self.title)

    def load_comments(self, **kwargs):
        self.comments = PostGateway().get_resource(self, 'comments', **kwargs)


class PostLike(Post):
    _schema = 'PostSchema'
    type_ = 'like'
