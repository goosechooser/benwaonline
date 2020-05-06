from marshmallow_jsonapi import fields
from benwaonline.schemas import BaseSchema

class CommentSchema(BaseSchema):
    id = fields.String()
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
