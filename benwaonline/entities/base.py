from marshmallow_jsonapi.fields import Relationship
from benwaonline import gateways as rf
from benwaonline.oauth import TokenAuth

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
    schema = None
    type_ = None
    attrs = None

    def __init__(self, id=None):
        self.id = id

    @classmethod
    def from_response(cls, response, many=False):
        '''Factory method.

        Args:
            response: a Response instance.
            many: optional variable, set True if response contains multiple resource objects.

        Returns:
            either a list of Entity instances (if many is True) or a single Entity instance
        '''
        entity, errors = cls.schema(many=many).load(response.json())
        return [cls(**e) for e in entity] if many else cls(**entity)

    @classmethod
    def from_included(cls, response, many=False):
        '''Factory method. Constructs entities from 'included' instead of 'data'

        Args:
            response: a Response instance.
            many: optional variable, set True if response contains multiple resource objects.

        Returns:
            either a list of Entity instances (if many is True) or a single Entity instance
        '''
        included = {
            'data': filter(lambda x: x['type'] == cls.type_, response.json()['included'])
        }
        entity, errors = cls.schema(many=many).load(included)
        return [cls(**e) for e in entity] if many else cls(**entity)

    def dump(self, many=False):
        '''Convenience method for dumping.'''
        return self.schema(many=many).dump(self.__dict__).data

    def dumps(self, many=False, data=None):
        '''Convenience method for dumping.

        Args:
            many: optional variable, set True if dumping multiple resource objects
            data: optional variable, if for whatever reason you don't want to dump the instance

        Returns:
            a JSON-API formatted resource object
        '''
        # This method is kinda sketchy/smelly
        # Refactor later
        to_dump = data or self.__dict__
        return self.schema(many=many).dumps(to_dump).data

    @property
    def relationships(self):
        return [k for k, v in self.schema._declared_fields.items() if isinstance(v, Relationship)]

    def nonempty_fields(self):
        return [v for v in self.schema._declared_fields.keys() if getattr(self, v)]

    @property
    def api_endpoint(self):
        return self.schema.Meta.self_url_many

    @property
    def instance_uri(self):
        return self.schema.Meta.self_url.replace('{id}', str(self.id))

    def resource_uri(self, other):
        try:
            related_field = self.attrs.get(other.type_, other.type_)
        except AttributeError:
            related_field = other
        related_url = self.schema._declared_fields[related_field].related_url
        return related_url.replace('{id}', str(self.id))

    def relationship_uri(self, other):
        # could move this out too, func then expects only a string
        try:
            related_field = self.attrs.get(other.type_, other.type_)
        except AttributeError:
            related_field = other
        self_url = self.schema._declared_fields[related_field].self_url
        return self_url.replace('{id}', str(self.id))

    def _add_to(self, obj, access_token):
        return rf.add_to(self, obj, TokenAuth(access_token))

    def _delete_from(self, obj, access_token):
        rf.delete_from(self, obj, TokenAuth(access_token))

    def _load_resource(self, obj, **kwargs):
        r = rf.get_resource(self, obj, **kwargs)
        resource = obj.from_response(r, many=True)
        setattr(self, self.attrs.get(obj.type_, obj.type_), resource)
