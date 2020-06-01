from flask_login import UserMixin
from benwaonline.gateways import UserGateway

from benwaonline.entities import Entity
from benwaonline.cache import cache

class User(Entity, UserMixin):
    '''Represents a User resource object, related to the User model in the database.

    Also used by flask-login, for authentication.

    Attributes:
        type_: 'user'

    '''
    _schema = 'UserSchema'
    type_ = 'user'

    attrs = {
        'post': 'posts',
        'comment': 'comments',
        'like': 'likes'
    }

    def __init__(self, id=None, username=None, created_on=None, user_id=None, active=None, comments=None, posts=None, likes=None):
        super().__init__(id=id)
        self.username = username
        self.created_on = created_on
        self.user_id = user_id
        self.active = active
        self.comments = comments or []
        self.posts = posts or []
        self.likes = likes or []

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def get_id(self):
        return self.user_id

    def like_post(self, post_id, access_token):
        r = UserGateway().like_post(self, post_id, access_token)

        if r.status_code == 200:
            self.likes.append(str(post_id))
            key = 'user_{}'.format(self.user_id)
            s = cache.set(key, self, timeout=3600)

        return r

    def unlike_post(self, post_id, access_token):
        r = UserGateway().unlike_post(self, post_id, access_token)

        if r.status_code == 200:
            self.likes.remove(str(post_id))
            key = 'user_{}'.format(self.user_id)
            s = cache.set(key, self, timeout=3600)

        return r

    def load_comments(self, **kwargs):
        self.comments = UserGateway().get_resource(self, 'comments', **kwargs)
        self.comments.sort(key=lambda comment: comment.created_on, reverse=True)

    def load_posts(self, **kwargs):
        self.posts = UserGateway().get_resource(self, 'posts', **kwargs)
        self.posts.sort(key=lambda post: post.created_on, reverse=True)

    def load_likes(self, **kwargs):
        self.likes = UserGateway().get_resource(self, 'likes', **kwargs)


class UserLike(User):
    type_ = 'likes'
