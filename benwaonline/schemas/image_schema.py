from marshmallow_jsonapi import fields
from benwaonline.schemas import BaseSchema

class ImageSchema(BaseSchema):
    id = fields.String()
    filepath = fields.Str()
    created_on = fields.DateTime()

    class Meta:
        type_ = 'images'
        self_url = '/api/images/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/images'