from marshmallow_jsonapi import fields
from benwaonline.schemas import BaseSchema

class PostSchema(BaseSchema):
    id = fields.String()
    title = fields.String()
    created_on = fields.DateTime()

    class Meta:
        type_ = 'posts'
        strict = False
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
        dump_only=True,
        type_='likes',
        self_url='/api/posts/{id}/relationships/likes',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/posts/{id}/likes',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='UserSchema'
    )

    likes = fields.Relationship(
        load_only=True,
        type_='users',
        self_url='/api/posts/{id}/relationships/likes',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/posts/{id}/likes',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='UserSchema'
    )