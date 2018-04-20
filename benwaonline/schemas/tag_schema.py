from marshmallow_jsonapi import fields
from benwaonline.schemas import BaseSchema

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
