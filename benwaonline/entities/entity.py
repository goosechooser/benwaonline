import os

from benwaonline import gateways as rf
from benwaonline import assemblers, mappers
from benwaonline.config import app_config
from benwaonline.oauth import TokenAuth

cfg = app_config[os.getenv('FLASK_CONFIG')]
API_URL = cfg.API_URL

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
    _schema = 'BaseSchema'
    type_ = 'base'
    attrs = None

    def __init__(self, id: str = None):
        self.id = id
        self.schema = assemblers.get_schema(self._schema)

    def dump(self, many: bool = False):
        '''Convenience method for dumping.'''
        return self.schema(many=many).dump(self.__dict__).data

    def dumps(self, many: bool = False, data: dict = None):
        '''Convenience method for dumping.

        Args:
            many: optional variable, set True if dumping multiple resource objects
            data: optional variable, if for whatever reason you don't want to dump the instance

        Returns:
            a JSON-API formatted resource object
        '''
        to_dump = data or self.__dict__
        return self.schema(many=many).dumps(to_dump).data

    # @property
    # def relationships(self):
    #     return [k for k, v in self.schema._declared_fields.items() if isinstance(v, Relationship)]

    # def nonempty_fields(self):
    #     return [v for v in self.schema._declared_fields.keys() if getattr(self, v)]

    # @property
    # def api_endpoint(self):
    #     return self.schema.Meta.self_url_many

    # @property
    # def instance_uri(self):
    #     return self.schema.Meta.self_url.replace('{id}', str(self.id))

    # def resource_uri(self, other):
    #     try:
    #         related_field = self.attrs.get(other.type_, other.type_)
    #     except AttributeError:
    #         related_field = other
    #     related_url = self.schema._declared_fields[related_field].related_url
    #     return related_url.replace('{id}', str(self.id))

    # def relationship_uri(self, other):
    #     # could move this out too, func then expects only a string
    #     try:
    #         related_field = self.attrs.get(other.type_, other.type_)
    #     except AttributeError:
    #         related_field = other
    #     self_url = self.schema._declared_fields[related_field].self_url
    #     return self_url.replace('{id}', str(self.id))

    def _add_to(self, resource: str, id: int, access_token: str):
        obj = assemblers.get_entity(resource)(id=id)
        uri = API_URL + mappers.relationship_uri(self, resource)
        return rf.add_to(uri, obj.dumps(many=True, data=[obj.__dict__]), TokenAuth(access_token))

    def _delete_from(self, resource: str, id: str, access_token: str):
        obj = assemblers.get_entity(resource)(id=id)
        uri = API_URL + mappers.relationship_uri(self, resource)
        return rf.delete_from(uri, obj.dumps(many=True, data=[obj.__dict__]), TokenAuth(access_token))

    def _load_resource(self, e: str, **kwargs):
        obj = assemblers.get_entity(e)
        uri = API_URL + mappers.resource_uri(self, e)
        r = rf.get_resource(uri, **kwargs)

        resource = assemblers.make_entity(e, r.json(), many=kwargs.get('many'))
        try:
            assemblers.load_included(resource, r.json()['included'], kwargs.get('include'))
        except KeyError:
            pass

        field = self.attrs.get(obj.type_, obj.type_)
        setattr(self, field, resource)
