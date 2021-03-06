import os
from typing import List

from benwaonline import mappers, assemblers
from benwaonline.gateways import Gateway, Parameter
from benwaonline.oauth import TokenAuth
from benwaonline.query import EntityQuery

API_URL = os.getenv('API_URL')

Entity = 'Entity'
Response = 'requests.Response'

def single(l: list):
    '''Returns one or None.'''
    try:
        return l[0]
    except IndexError:
        return None

class EntityGateway(Gateway):
    _entity = 'entity'
    def __init__(self):
        self.entity = assemblers.get_entity(self._entity)
        self.schema = assemblers.get_schema(self.entity._schema)

    def get(self, **kwargs) -> List[Entity]:
        '''
        Builds and executes a GET request for the collection of a resource

        Args:
            obj: is the Entity of the resource desired
            page_size: (optional) the number of results returned, 0 is all of the resources
            **kwargs: Arbitrary keyword arguments.

        Returns:
            a list of Entity.
        '''
        uri = API_URL + mappers.collection_uri(self.entity())
        params = Parameter(**kwargs)
        r = self._get(uri, params.dump())

        e = assemblers.from_response(self.entity.type_, r.json(), many=True, include=params.include)

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
        params = Parameter(**kwargs)

        r = self._get(uri, params.dump())
        e = assemblers.from_response(self.entity.type_, r.json(), include=params.include)

        return e

    def get_resource(self, e: Entity, r: str, **kwargs) -> Entity:
        uri = API_URL + mappers.resource_uri(e, r)
        params = Parameter(**kwargs)

        resp = self._get(uri, params.dump())
        many = mappers.many(e, r)
        resource = assemblers.from_response(r, resp.json(), many=many, include=params.include)

        return resource

    def _filter(self, e: Entity, **kwargs) -> Entity:
        uri = API_URL + mappers.collection_uri(e)
        q = EntityQuery(e)

        params = Parameter(filters=q.to_filter(), **kwargs)
        return self._get(uri, params.dump())

    def new(self, access_token: str, **kwargs) -> Entity:
        e = self.entity(id=666, **kwargs)
        include = [r for r in mappers.relationships(e) if getattr(e, r)]

        r = self._new(e, access_token)

        return assemblers.from_response(self.entity.type_, r.json(), include=include)

    def _new(self, e: Entity, access_token: str) -> Entity:
        uri = API_URL + mappers.collection_uri(e)
        include = [r for r in mappers.relationships(e) if getattr(e, r)]
        params = Parameter(include=include)

        auth = TokenAuth(access_token)

        return self._post(uri, e.dumps(), auth, params=params.dump())

    def delete(self, e: Entity, access_token: str) -> Response:
        uri = API_URL + mappers.instance_uri(e)
        auth = TokenAuth(access_token)

        return self._delete(uri, auth)

    def add_to(self, e: Entity, resource: Entity, access_token: str) -> Response:
        '''
        Builds and executes a POST request for a one-to-many resource relationship.
        Use this if you want to add a resource to a one-to-many relationship, instead of replacing it completely.
        '''
        uri = API_URL + mappers.relationship_uri(e, e._attrs(resource))
        data = resource.dumps(many=True, data=[resource.__dict__])
        auth = TokenAuth(access_token)

        return self._post(uri, data, auth)

    def delete_from(self, e: Entity, resource: Entity, access_token: str) -> Response:
        '''
        Builds and executes a DELETE request for a to-many resource relationship.
        Use this if you want to remove a resource to a to-many relationship.
        '''
        uri = API_URL + mappers.relationship_uri(e, e._attrs(resource))
        data = resource.dumps(many=True, data=[resource.__dict__])
        auth = TokenAuth(access_token)

        return self._delete(uri, auth, data=data)
