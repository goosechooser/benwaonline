from benwaonline import gateways as rf
from benwaonline.query import EntityQuery
from benwaonline.oauth import TokenAuth

def single(entity):
    try:
        return entity[0]
    except IndexError:
        return None

class EntityGateway(object):
    def __init__(self, entity):
        self.entity = entity

    def get(self, result_size=100, **kwargs):
        entities = self.entity()
        r = self._get(entities, page_opts={'size': result_size}, **kwargs)

        return entities.from_response(r, many=True)

    def get_by_id(self, id, **kwargs):
        entity = self.entity(id=id)
        r = self._get_by_id(entity, **kwargs)

        return entity.from_response(r)

    def get_resource(self, entity, resource, result_size=20, **kwargs):
        r = self._get_resource(entity, resource, **kwargs)

        return resource.from_response(r, many=True)

    def new(self, access_token, **kwargs):
        entity = self.entity(**kwargs)
        r = self._new(entity, access_token)

        return self.entity.from_response(r)

    def _get(self, entity, **kwargs):
        return rf.get(entity, **kwargs)

    def _get_by_id(self, entity, **kwargs):
        return rf.get_instance(entity, **kwargs)

    def _get_resource(self, entity, other, **kwargs):
        return rf.get_resource(entity, other, **kwargs)

    def _new(self, entity, access_token):
        auth = TokenAuth(access_token)
        return rf.post(entity, auth)

    def _delete(self, entity, access_token):
        auth = TokenAuth(access_token)
        return rf.delete(entity, auth)

    def _filter(self, entity, **kwargs):
        q = EntityQuery(entity)
        return rf.filter(entity, q, **kwargs)
