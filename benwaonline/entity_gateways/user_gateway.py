from benwaonline.assemblers import make_entity, load_included, get_entity
from benwaonline.entity_gateways import EntityGateway, single

Entity = 'Entity'

class UserGateway(EntityGateway):
    _entity = 'user'

    def get_by_user_id(self, user_id):
        user = self.entity(user_id=user_id)
        r = self._filter(user)

        return single(make_entity('user', r.json(), many=True))

    def get_by_username(self, username):
        user = self.entity(username=username)
        r = self._filter(user)

        return single(make_entity('user', r.json(), many=True))

    def new(self, username: str, access_token: str) -> Entity:
        user = self.entity(username=username)
        r = self._new(user, access_token)

        return make_entity('user', r.json())
