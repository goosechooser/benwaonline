import os
from typing import List

from benwaonline import gateways as rf
from benwaonline import mappers
from benwaonline import assemblers
from benwaonline.config import app_config
from benwaonline.oauth import TokenAuth
from benwaonline.query import EntityQuery

cfg = app_config[os.getenv('FLASK_CONFIG')]
API_URL = cfg.API_URL

Entity = 'Entity'
Response = 'requests.Response'

def single(l: list):
    '''Returns one or None.'''
    try:
        return l[0]
    except IndexError:
        return None

class EntityGateway(object):
    _entity = 'entity'
    def __init__(self):
        self.entity = assemblers.get_entity(self._entity)
        self.schema = assemblers.get_schema(self.entity._schema)

    def get(self, result_size: int = 100, **kwargs) -> List[Entity]:
        '''
        Builds and executes a GET request for the collection of a resource

        Args:
            obj: is the Entity of the resource desired
            result_size: (optional) the number of results returned, 0 is all of the resources
            **kwargs: Arbitrary keyword arguments.

        Returns:
            a list of Entity.
        '''
        uri = API_URL + mappers.collection_uri(self.entity())

        r = self._get(uri, page_opts={'size': result_size}, **kwargs)
        e = assemblers.make_entity(self.entity.type_, r.json(), many=True)

        try:
            assemblers.load_included(e, r.json()['included'], kwargs.get('include'))
        except KeyError:
            pass

        return e

    def get_by_id(self, id: int, **kwargs) -> Entity:
        '''
        Builds and executes a GET request for a single resource.

        Args:
            id: is the id of the resource desired
            **kwargs: Arbitrary keyword arguments

        Returns:
            an Entity.
        '''
        e = self.entity(id=id)
        uri = API_URL + mappers.instance_uri(e)

        r = self._get(uri, **kwargs)
        e = assemblers.make_entity(self.entity.type_, r.json())

        try:
            assemblers.load_included([e], r.json()['included'], kwargs.get('include'))
        except KeyError:
            pass

        return e

    def get_resource(self, id: int, r: str, result_size: int = 20, **kwargs) -> Entity:
        uri = API_URL + mappers.resource_uri(self.entity(id=id), r)

        r = self._get(uri, **kwargs)

        return assemblers.make_entity(r, r.json(), many=kwargs.get('many'))

    def new(self, access_token: str, **kwargs) -> Entity:
        entity = self.entity(**kwargs)
        entity.id = 666

        r = self._new(entity, access_token)

        return assemblers.make_entity(self.entity.type_, r.json())

    def _get(self, uri: str, **kwargs) -> Response:
        params = rf.prepare_params(**kwargs)

        return rf.request('get', uri, params=params)

    def _get_by_id(self, e: Entity, **kwargs) -> Response:
        uri = API_URL + mappers.instance_uri(e)

        return rf.get_instance(uri, **kwargs)

    def _get_resource(self, e: Entity, resource: Entity, **kwargs) -> Response:
        uri = API_URL + mappers.resource_uri(e, resource)

        return rf.get_resource(uri, **kwargs)

    def _new(self, e: Entity, access_token: str) -> Response:
        uri = API_URL + mappers.collection_uri(e)
        include = [r for r in mappers.relationships(e) if getattr(e, r)]

        auth = TokenAuth(access_token)

        return rf.post(uri, e.dumps(), include, auth)

    def _delete(self, e: Entity, access_token: str) -> Response:
        uri = API_URL + mappers.instance_uri(e)
        auth = TokenAuth(access_token)

        return rf.delete(uri, auth)

    def _filter(self, e: Entity, **kwargs) -> Response:
        uri = API_URL + mappers.collection_uri(e)
        q = EntityQuery(e)
        return rf.filter(uri, q, **kwargs)
