from marshmallow_jsonapi import fields
from benwaonline.schemas import BaseSchema

class UserSchema(BaseSchema):
    id = fields.String()
    username = fields.String()
    created_on = fields.DateTime()
    user_id = fields.String()
    active = fields.Boolean(load_from='is_active', dump_to='is_active')

    class Meta:
        type_ = 'users'
        strict = False
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
        dump_only=True,
        type_='likes',
        self_url='/api/users/{id}/relationships/likes',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/users/{id}/likes',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='PostSchema'
    )

    likes = fields.Relationship(
        load_only=True,
        type_='posts',
        self_url='/api/users/{id}/relationships/likes',
        self_url_kwargs={'id': '<id>'},
        related_url='/api/users/{id}/likes',
        related_url_kwargs={'id': '<id>'},
        many=True,
        include_resource_linkage=True,
        schema='PostSchema'
    )