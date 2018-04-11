from benwaonline.entities import Tag
from .base import EntityGateway, single

class TagGateway(EntityGateway):
    def __init__(self):
        super().__init__(Tag)

    def get_by_name(self, name):
        tag = self.entity(name=name)
        r = self._filter(tag)

        return single(tag.from_response(r, many=True))

    def new(self, name, access_token):
        tag = self.entity(name=name)
        r = self._new(tag, access_token)

        return tag.from_response(r)
