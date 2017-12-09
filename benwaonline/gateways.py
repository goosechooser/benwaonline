import json
import requests
from benwaonline import schemas
from marshmallow import pprint

class BenwaGateway(object):
    HEADERS = {
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json'
    }

    def __init__(self, api_endpoint, schema):
        self.api_endpoint = api_endpoint
        self.schema = schema

    def get(self, _id=None, include=None):
        '''
        include is a list of strings containing the attributes you want
        something something compound document
        '''
        if _id:
            uri = '/'.join([self.api_endpoint, str(_id)])
            many = False
        else:
            uri = self.api_endpoint
            many = True

        try:
            params = {'include': ','.join(include)}
        except TypeError:
            params = {}
        r = requests.get(uri, headers=self.HEADERS, params=params, timeout=5)
        r.raise_for_status()

        return self.schema(many=many).load(r.json()).data

    def post(self, data, auth):
        obj = dict({'id': '666'}, **data)
        payload = self.schema().dumps(obj).data
        r = requests.post(self.api_endpoint, data=payload, headers=self.HEADERS, timeout=5, auth=auth)
        # r.raise_for_status()
        return self.schema().load(r.json()).data

    def filter(self, filters, single=False, include=None):
        many = True

        try:
            params = {'include': ','.join(include)}
        except TypeError:
            params = {}

        if single:
            params['filter[single]'] = 1
            many = False

        params['filter[objects]'] = json.dumps(filters)
        r = requests.get(self.api_endpoint, headers=self.HEADERS, params=params, timeout=5)
        r.raise_for_status()
        return self.schema(many=many).load(r.json()).data

    def patch(self, _id, attribute, data, auth):
        # If we made some objects we could merge attribute/data into that
        # like {'type': 'previews', 'data': data} etc
        uri = '/'.join([self.api_endpoint, str(_id), 'relationships', attribute])
        r = requests.patch(uri, headers=self.HEADERS, data=data, timeout=5, auth=auth)
        return r

    def add_to(self, resource_endpoint, _id, attribute, data, auth):
        '''
            Adds resource to a 'to-many' relationship
            Needs a better name imo
            Needs a better function header while we're at it
        '''
        if not isinstance(data, list):
            data = [data]

        patch = self.schema(many=True).dumps(data).data
        uri = '/'.join([resource_endpoint, str(_id), 'relationships', attribute])
        r = requests.post(uri, headers=self.HEADERS, data=patch, timeout=5, auth=auth)
        return r

    def delete(self, _id, auth):
        uri = '/'.join([self.api_endpoint, str(_id)])
        r = requests.delete(uri, headers=self.HEADERS, timeout=5, auth=auth)
        r.raise_for_status()
        return

class PostGateway(BenwaGateway):
    def __init__(self, api_endpoint, schema=schemas.PostSchema):
        super().__init__(api_endpoint, schema)

class UserGateway(BenwaGateway):
    def __init__(self, api_endpoint, schema=schemas.UserSchema):
        super().__init__(api_endpoint, schema)

class PreviewGateway(BenwaGateway):
    def __init__(self, api_endpoint, schema=schemas.PreviewSchema):
        super().__init__(api_endpoint, schema)

class ImageGateway(BenwaGateway):
    def __init__(self, api_endpoint, schema=schemas.ImageSchema):
        super().__init__(api_endpoint, schema)

class TagGateway(BenwaGateway):
    def __init__(self, api_endpoint, schema=schemas.TagSchema):
        super().__init__(api_endpoint, schema)

class CommentGateway(BenwaGateway):
    def __init__(self, api_endpoint, schema=schemas.CommentSchema):
        super().__init__(api_endpoint, schema)