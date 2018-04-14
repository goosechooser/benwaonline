from flask_login import UserMixin
from benwaonline import gateways as rf
from benwaonline.schemas import UserSchema
# from benwaonline.assemblers import get_entity, make_entity, load_included

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
        return self._add_to('likes', post_id, access_token)

    def unlike_post(self, post_id, access_token):
        return self._delete_from('likes', post_id, access_token)

    def load_comments(self, **kwargs):
        self._load_resource('comments', many=True, **kwargs)

    def load_posts(self, result_size=20, **kwargs):
        self._load_resource('posts', many=True, page_opts={'size': result_size}, **kwargs)

    def load_likes(self, result_size=20, **kwargs):
        self._load_resource('likes', many=True, page_opts={'size': result_size}, **kwargs)


class UserLike(User):
    type_ = 'likes'
