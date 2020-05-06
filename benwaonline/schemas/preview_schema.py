from marshmallow_jsonapi import fields
from benwaonline.schemas import BaseSchema

class PreviewSchema(BaseSchema):
    id = fields.String()
    filepath = fields.Str()
    created_on = fields.DateTime()

    class Meta:
        type_ = 'previews'
        self_url = '/api/previews/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/api/previews'