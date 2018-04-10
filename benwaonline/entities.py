import os

from flask_login import UserMixin
from marshmallow_jsonapi.fields import Relationship
from requests.exceptions import HTTPError

from benwaonline import schemas
from benwaonline.config import app_config
from benwaonline import gateways as rf
from benwaonline.entity_gateway import LikeGateway, PostGateway, UserGateway, handle_response_error
from benwaonline.exceptions import BenwaOnlineRequestError

cfg = app_config[os.getenv('FLASK_CONFIG')]
API_URL = cfg.API_URL

# These are the 'Domain Objects'
# the schemas are the 'Domain Transfer Objects'

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
        entity, errors = cls.schema(many=many).load(response.json())
        return [cls(**e) for e in entity] if many else cls(**entity)

    @classmethod
    def from_included(cls, response, many=False):
        '''Factory method. Constructs entities from 'included' instead of 'data'

        Args:
            response: a Response instance.
            many: optional variable, set True if response contains multiple resource objects.

        Returns:
            either a list of Entity instances (if many is True) or a single Entity instance
        '''
        included = {
            'data': filter(lambda x: x['type'] == cls.type_, response.json()['included'])
        }
        entity, errors = cls.schema(many=many).load(included)
        return [cls(**e) for e in entity] if many else cls(**entity)

    def dump(self, many=False):
        '''Convenience method for dumping.'''
        return self.schema(many=many).dump(self.__dict__).data

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
    def relationships(self):
        return [k for k, v in self.schema._declared_fields.items() if isinstance(v, Relationship)]

    def nonempty_fields(self):
        return [v for v in self.schema._declared_fields.keys() if getattr(self, v)]

    @property
    def api_endpoint(self):
        return self.schema.Meta.self_url_many

    @property
    def instance_uri(self):
        return self.schema.Meta.self_url.replace('{id}', str(self.id))

    def resource_uri(self, other):
        try:
            related_field = self.attrs.get(other.type_, other.type_)
        except AttributeError:
            related_field = other
        related_url = self.schema._declared_fields[related_field].related_url
        return related_url.replace('{id}', str(self.id))

    def relationship_uri(self, other):
        # could move this out too, func then expects only a string
        try:
            related_field = self.attrs.get(other.type_, other.type_)
        except AttributeError:
            related_field = other
        self_url = self.schema._declared_fields[related_field].self_url
        return self_url.replace('{id}', str(self.id))

    def _load_resource(self, gateway, obj, **kwargs):
        try:
            resource = gateway().get_resource(self, obj, **kwargs)
        except BenwaOnlineRequestError as err:
            raise err
            
        setattr(self, self.attrs.get(obj.type_, obj.type_), resource)


class Post(Entity):
    '''Represents a Post resource object, related to the Post model in the database

    Attributes:
        type_: 'posts'

    '''
    schema = schemas.PostSchema
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

class Like(Entity):
    schema = schemas.LikeSchema
    type_ = schema.Meta.type_

    def __init__(self, id=None):
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

    # def _add_to(self, obj, access_token):
    # def _load_resource(self, resource):
    #     return
    def like_post(self, post_id, access_token):
        like = PostLike(id=post_id)
        try:
            return LikeGateway().new(self, like, access_token)
        except BenwaOnlineRequestError as err:
            print(err)
            # msg = '{}'.format(err)
            # current_app.logger.debug(msg)

    def unlike_post(self, post_id, access_token):
        like = PostLike(id=post_id)
        try:
            return LikeGateway().delete(self, like, access_token)
        except BenwaOnlineRequestError as err:
            print(err)
            # msg = '{}'.format(err)
            # current_app.logger.debug(msg)

    def load_comments(self, **kwargs):
        self._load_resource(UserGateway, Comment(), **kwargs)

    def load_posts(self, **kwargs):
        self._load_resource(UserGateway, Post(), **kwargs)

    def load_likes(self, **kwargs):
        self._load_resource(UserGateway, PostLike(), **kwargs)

class UserLike(User):
    type_ = 'likes'

class Image(Entity):
    '''Represents a Image resource object, related to the Image model in the database

    Attributes:
        type_: 'images'

    '''
    schema = schemas.ImageSchema
    type_ = schema.Meta.type_
    attrs = {}

    def __init__(self, id=None, filepath=None, created_on=None):
        self.id = id
        self.filepath = filepath
        self.created_on = created_on


class Preview(Image):
    '''Represents a Preview resource object, related to the Preview model in the database

    Attributes:
        type_: 'previews'

    '''
    schema = schemas.PreviewSchema
    type_ = schema.Meta.type_
    attrs = {}

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

    def __init__(self, id=None, content=None, created_on=None, user=None, post=None, poster=None, metadata=None):
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

    def __init__(self, id=None, name=None, created_on=None, posts=None, num_posts=0):
        self.id = id
        self.name = name
        self.created_on = created_on
        self.posts = posts or []
        self.num_posts = num_posts

    def __repr__(self):
        return '<Like {} - {}>'.format(self.id, self.name)
