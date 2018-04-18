from benwaonline.assemblers import get_entity, make_entity
from benwaonline.entity_gateways import EntityGateway

class PostGateway(EntityGateway):
    _entity = 'post'

    def tagged_with(self, tag_names, **kwargs):
        '''Returns all Posts that are tagged with any of the given tags.'''
        e = get_entity('tag')
        tags = [e(name=tag) for tag in tag_names]
        posts = self.entity(tags=tags)
        r = self._filter(posts, **kwargs)

        return make_entity(self.entity.type_, r.json(), many=True)
