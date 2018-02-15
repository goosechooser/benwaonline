import os
from requests.exceptions import HTTPError
from flask_login import UserMixin
from benwaonline import schemas

from benwaonline.config import app_config
cfg = app_config[os.getenv('FLASK_CONFIG')]
API_URL = cfg.API_URL

class Entity(object):
    '''Represents JSON-API resource object(s)

    Encapsulates serializing and deserializing of JSON-API resource objects.
    Contains api endpoint information.

    You'll never use this class directly.

    Attributes:
        schema: a marshmallow-jsonapi Schema.
        type_: the 'type' of the Entity
        attrs: a dict. Sometimes the class attribute name and the type_ name differ.
            This can cause issues when we build our urls.
            ex: a Post has a 'user' attribute of type_ 'users'
                we want an url like '/posts/{post_id}/user' not '/posts/{post_id}/users'
    '''
    # Had difficulty describing what this object is for
    # Defs need to think about refactoring
    schema = None
    type_ = None
    attrs = None

    @classmethod
    def from_response(cls, response, many=False):
        '''Factory method.

        Args:
            response: a Response instance.
            many: optional variable, set True if response contains multiple resource objects.

        Returns:
            either a list of Entity instances (if many is True) or a single Entity instance
        '''
        try:
            response.raise_for_status()
        except HTTPError:
            return None
        else:
            entity, errors = cls.schema(many=many).load(response.json())
            return [cls(**e) for e in entity] if many else cls(**entity)

    def dumps(self, many=False, data=None):
        '''Convenience method for dumping.

        Args:
            many: optional variable, set True if dumping multiple resource objects
            data: optional variable, if for whatever reason you don't want to dump the instance

        Returns:
            a JSON-API formatted resource object
        '''
        # This method is kinda sketchy/smelly
        # Refactor later
        to_dump = data or self.__dict__
        return self.schema(many=many).dumps(to_dump).data

    @property
    def api_endpoint(self):
        return '/'.join([API_URL, self.type_])

    @property
    def instance_uri(self):
        return '/'.join([self.api_endpoint, str(self.id)])

    @property
    def relationship_uri_base(self):
        return '/'.join([self.api_endpoint, str(self.id), 'relationships'])

    def resource_uri(self, other):
        return '/'.join([self.instance_uri, self.attrs.get(other.type_, other.type_)])

    def relationship_uri(self, other):
        return '/'.join([self.relationship_uri_base, self.attrs.get(other.type_, other.type_)])

class Post(Entity):
    '''Represents a Post resource object, related to the Post model in the database

    Attributes:
        type_: 'posts'

    '''
    schema = schemas.PostSchema
    type_ = schema.Meta.type_

    attrs = {
        'previews': 'preview',
        'images': 'image',
        'users': 'user'
    }

    def __init__(self, id=666, title=None, created_on=None, user=None, comments=None, image=None, preview=None, tags=None, likes=None):
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


class Like(Entity):
    schema = schemas.PostSchema
    type_ = schema.Meta.type_

    def __init__(self, id=666):
        self.id = id

    def __repr__(self):
        return '<Like {}>'.format(self.id)

class User(Entity, UserMixin):
    '''Represents a User resource object, related to the User model in the database.

    Also used by flask-login, for authentication.

    Attributes:
        type_: 'users'

    '''
    schema = schemas.UserSchema
    type_ = schema.Meta.type_

    attrs = {}

    def __init__(self, id=666, username=None, created_on=None, user_id=None, active=None, comments=None, posts=None, likes=None):
        super().__init__()
        self.id = id
        self.username = username
        self.created_on = created_on
        self.user_id = user_id
        self.active = active
        self.comments = comments or []
        self.posts = posts or []
        self.likes = likes or []

class Image(Entity):
    '''Represents a Image resource object, related to the Image model in the database

    Attributes:
        type_: 'images'

    '''
    schema = schemas.ImageSchema
    type_ = schema.Meta.type_
    attrs = {}

    def __init__(self, id=666, filepath=None, created_on=None):
        self.id = id
        self.filepath = filepath
        self.created_on = created_on

class Preview(Entity):
    '''Represents a Preview resource object, related to the Preview model in the database

    Attributes:
        type_: 'previews'

    '''
    schema = schemas.PreviewSchema
    type_ = schema.Meta.type_
    attrs = {}

    def __init__(self, id=666, filepath=None, created_on=None):
        self.id = id
        self.filepath = filepath
        self.created_on = created_on

class Comment(Entity):
    '''Represents a Comment resource object, related to the Comment model in the database

    Attributes:
        type_: 'comments'

    '''
    schema = schemas.CommentSchema
    type_ = schema.Meta.type_
    attrs = {
        'posts': 'post',
        'users': 'user'
    }

    def __init__(self, id=666, content=None, created_on=None, user=None, post=None, poster=None, metadata=None):
        self.id = id
        self.content = content
        self.created_on = created_on
        self.user = user
        self.post = post
        self.poster = poster
        self.metadata = metadata

class Tag(Entity):
    '''Represents a Tag resource object, related to the Tag model in the database

    Attributes:
        type_: 'Tag'

    '''
    schema = schemas.TagSchema
    type_ = schema.Meta.type_
    attrs = {}

    def __init__(self, id=666, name=None, created_on=None, posts=None, num_posts=0):
        self.id = id
        self.name = name
        self.created_on = created_on
        self.posts = posts or []
        self.num_posts = num_posts
