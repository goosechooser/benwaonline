from benwaonline.gateways import EntityGateway, single
from benwaonline.assemblers import make_entity

class TagGateway(EntityGateway):
    _entity = 'tag'

    def get_by_name(self, name):
        tag = self.entity(name=name)
        r = self._filter(tag)
        e = make_entity(self.entity.type_, r.json(), many=True)

        return single(e)

    def new(self, name, access_token):
        tag = self.entity(name=name)
        r = self._new(tag, access_token)

        return tag.from_response(r)
