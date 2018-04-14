from benwaonline.assemblers import get_entity, make_entity
from benwaonline.entity_gateways import EntityGateway

class PostGateway(EntityGateway):
    _entity = 'post'

    # def new(self, access_token, **kwargs):
    #     post = self.entity(**kwargs)
    #     r = self._new(post, access_token)

    #     return Post.from_response(r)

    def tagged_with(self, tag_names, result_size=100, **kwargs):
        '''Returns all Posts that are tagged with any of the given tags.'''
        e = get_entity('tag')
        tags = [e(name=tag) for tag in tag_names]
        posts = self.entity(tags=tags)
        r = self._filter(posts, page_opts={'size': result_size}, **kwargs)

        return make_entity(self.entity.type_, r.json(), many=True)
