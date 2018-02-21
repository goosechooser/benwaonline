from marshmallow import post_load, pre_dump
from marshmallow_jsonapi import Schema, fields

class BaseSchema(Schema):

    @pre_dump
    def clean(self, data):
        # Filter out keys with null values
        return dict((k, v) for k, v in data.items() if v)

class PreviewSchema(BaseSchema):
    id = fields.Int()
    filepath = fields.Str()
    created_on = fields.DateTime()

    class Meta:
        type_ = 'previews'
        self_url = '/api/previews/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/previews'

class ImageSchema(BaseSchema):
    id = fields.Int()
    filepath = fields.Str()
    created_on = fields.DateTime()

    class Meta:
        type_ = 'images'
        self_url = '/api/images/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/images'

class CommentSchema(BaseSchema):
    id = fields.Int()
    content = fields.String()
    created_on = fields.DateTime()
    poster = fields.String(load_only=True)

    class Meta:
        type_ = 'comments'
        self_url = '/api/comments/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/comments'

    user = fields.Relationship(
        type_='users',
        self_url = '/api/comments/{id}/relationships/user',
        self_url_kwargs = {'id': '<id>'},
        related_url='/api/comments/{id}/user',
        related_url_kwargs={'id': '<id>'},
        include_resource_linkage=True,
        schema='UserSchema'
    )

    post = fields.Relationship(
        type_='posts',
        self_url = '/api/comments/{id}/relationships/post',
        self_url_kwargs = {'id': '<id>'},
        related_url='/api/comments/{id}/post',
        related_url_kwargs={'id': '<id>'},
        include_resource_linkage=True,
        schema='PostSchema'
    )

class UserSchema(BaseSchema):
    id = fields.Int()
    username = fields.String()
    created_on = fields.DateTime()
    user_id = fields.String(dump_only=True)
    active = fields.Boolean(load_from='is_active', dump_to='is_active')

    class Meta:
        type_ = 'users'
        self_url = '/api/users/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/users'

    comments = fields.Relationship(
        type_='comments',
        self_url = '/api/users/{id}/relationships/comments',
        self_url_kwargs = {'id': '<id>'},
        related_url = '/api/users/{id}/comments',
        related_url_kwargs = {'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='CommentSchema'
    )

    posts = fields.Relationship(
        type_='posts',
        self_url = '/api/users/{id}/relationships/posts',
        self_url_kwargs = {'id': '<id>'},
        related_url = '/api/users/{id}/posts',
        related_url_kwargs = {'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='PostSchema'
    )

    likes = fields.Relationship(
        type_='likes',
        self_url='/api/users/{id}/relationships/likes',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/users/{id}/likes',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='LikeSchema'
    )

class PostSchema(BaseSchema):
    id = fields.Int()
    title = fields.String()
    created_on = fields.DateTime()

    class Meta:
        type_ = 'posts'
        self_url = '/api/posts/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/posts'

    user = fields.Relationship(
        type_='users',
        self_url = '/api/posts/{id}/relationships/user',
        self_url_kwargs = {'id': '<id>'},
        related_url='/api/posts/{id}/user',
        related_url_kwargs={'id': '<id>'},
        include_resource_linkage=True,
        schema='UserSchema'
    )

    comments = fields.Relationship(
        type_='comments',
        self_url='/api/posts/{id}/relationships/comments',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/posts/{id}/comments',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='CommentSchema'
    )

    image = fields.Relationship(
        type_='images',
        self_url = '/api/posts/{id}/relationships/image',
        self_url_kwargs = {'id': '<id>'},
        related_url='/api/posts/{id}/image',
        related_url_kwargs={'id': '<id>'},
        include_resource_linkage=True,
        schema='ImageSchema'
    )

    preview = fields.Relationship(
        type_='previews',
        self_url = '/api/posts/{id}/relationships/preview',
        self_url_kwargs = {'id': '<id>'},
        related_url='/api/posts/{id}/preview',
        related_url_kwargs={'id': '<id>'},
        include_resource_linkage=True,
        schema='PreviewSchema'
    )

    tags = fields.Relationship(
        type_='tags',
        self_url='/api/posts/{id}/relationships/tags',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/posts/{id}/tags',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='TagSchema'
    )

    likes = fields.Relationship(
        type_='likes',
        self_url='/api/posts/{id}/relationships/likes',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/posts/{id}/likes',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='LikeSchema'
    )

class LikeSchema(Schema):
    id = fields.String()
    class Meta:
        type_ = 'likes'

class TagSchema(BaseSchema):
    id = fields.String()
    name = fields.String()
    created_on = fields.DateTime()
    num_posts = fields.Int()

    class Meta:
        type_ = 'tags'
        self_url = '/api/tags/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/tags'

    posts = fields.Relationship(
        type_='posts',
        self_url = '/api/tags/{id}/relationships/posts',
        self_url_kwargs = {'id': '<id>'},
        related_url = '/api/tags/{id}/posts',
        related_url_kwargs = {'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='PostSchema'
    )
