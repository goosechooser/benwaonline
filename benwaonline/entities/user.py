from flask_login import UserMixin

from benwaonline import gateways as rf
from benwaonline.oauth import TokenAuth
from benwaonline.schemas import UserSchema

from .base import Entity
from .post import Post, PostLike
from .comment import Comment

class User(Entity, UserMixin):
    '''Represents a User resource object, related to the User model in the database.

    Also used by flask-login, for authentication.

    Attributes:
        type_: 'users'

    '''
    schema = UserSchema
    type_ = schema.Meta.type_

    attrs = {}

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
        like = PostLike(id=post_id)

        return rf.add_to(self, like, TokenAuth(access_token))

    def unlike_post(self, post_id, access_token):
        like = PostLike(id=post_id)

        return rf.delete_from(self, like, TokenAuth(access_token))

    def load_comments(self, **kwargs):
        self._load_resource(Comment(), **kwargs)

    def load_posts(self, result_size=20, **kwargs):
        self._load_resource(Post(), page_opts={'size': result_size}, **kwargs)

    def load_likes(self, result_size=20, **kwargs):
        self._load_resource(PostLike(), page_opts={'size': result_size}, **kwargs)

class UserLike(User):
    type_ = 'likes'
