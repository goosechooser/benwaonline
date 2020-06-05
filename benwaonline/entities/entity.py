import os

from benwaonline import assemblers, mappers
from benwaonline.oauth import TokenAuth

API_URL = os.getenv('API_URL')

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

    def _attrs(self, field):
        return self.attrs.get(field.type_, field.type_)

    def dump(self, many: bool = False):
        '''Convenience method for dumping.'''
        return self.schema(many=many).dump(self.__dict__)

    def dumps(self, many: bool = False, data: dict = None):
        '''Convenience method for dumping.

        Args:
            many: optional variable, set True if dumping multiple resource objects
            data: optional variable, if for whatever reason you don't want to dump the instance

        Returns:
            a JSON-API formatted resource object
        '''
        to_dump = data or self.__dict__
        return self.schema(many=many).dumps(to_dump)
