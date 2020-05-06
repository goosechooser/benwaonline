from marshmallow import pre_load, pre_dump
from marshmallow_jsonapi import Schema

class BaseSchema(Schema):
    @pre_load
    def id_str(self, data):
        try:
            data['id'] = str(data['id'])
        except KeyError:
            pass

    @pre_dump
    def clean(self, data):
        # Filter out keys with null values
        try:
            data['id'] = str(data['id'])
        except KeyError:
            pass
        return dict((k, v) for k, v in data.items() if v)