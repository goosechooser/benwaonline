from benwaonline.schemas import TagSchema
from benwaonline.entities import Entity

class Tag(Entity):
    '''Represents a Tag resource object, related to the Tag model in the database

    Attributes:
        type_: 'Tag'

    '''
    _schema = 'TagSchema'
    type_ = 'tag'
    attrs = {
        'post': 'posts'
    }

    def __init__(self, id=None, name=None, created_on=None, posts=None, num_posts=0):
        self.name = name
        self.created_on = created_on
        self.posts = posts or []
        self.num_posts = num_posts
        super().__init__(id=id)

    def __repr__(self):
        return '<Tag {} - {}>'.format(self.id, self.name)
