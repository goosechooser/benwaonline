from benwaonline.entities import User

from .base import EntityGateway, single

class UserGateway(EntityGateway):
    def __init__(self):
        super().__init__(User)

    def get_by_user_id(self, user_id):
        user = self.entity(user_id=user_id)
        r = self._filter(user)

        return single(self.entity.from_response(r, many=True))

    def get_by_username(self, username):
        user = self.entity(username=username)
        r = self._filter(user)

        return single(self.entity.from_response(r, many=True))

    def new(self, username, access_token):
        user = self.entity(username=username)
        r = self._new(user, access_token)

        return user.from_response(r)
