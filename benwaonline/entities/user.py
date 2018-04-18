from flask_login import UserMixin
from benwaonline.entity_gateways import UserGateway

from benwaonline.entities import Entity

class User(Entity, UserMixin):
    '''Represents a User resource object, related to the User model in the database.

    Also used by flask-login, for authentication.

    Attributes:
        type_: 'users'

    '''
    _schema = 'UserSchema'
    type_ = 'user'

    attrs = {
        'post': 'posts',
        'comment': 'comments',
        'like': 'likes'
    }

    def __init__(self, id=None, username=None, created_on=None, user_id=None, active=None, comments=None, posts=None, likes=None):
        super().__init__()
        self.id = id
        self.username = username
        self.created_on = created_on
        self.user_id = user_id
        self.active = active
        self.comments = comments or []
        self.posts = posts or []
        self.likes = likes or []

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def like_post(self, post_id, access_token):
        return UserGateway().like_post(self, post_id, access_token)

    def unlike_post(self, post_id, access_token):
        return UserGateway().unlike_post(self, post_id, access_token)

    def load_comments(self, **kwargs):
        self.comments = UserGateway().get_resource(self, 'comments', **kwargs)

    def load_posts(self, **kwargs):
        self.posts = UserGateway().get_resource(self, 'posts', **kwargs)

    def load_likes(self, **kwargs):
        self.likes = UserGateway().get_resource(self, 'likes', **kwargs)


class UserLike(User):
    type_ = 'likes'
