from benwaonline.entities import Post
from benwaonline.entity_gateways import EntityGateway
from benwaonline.assemblers import make_entity

class CommentGateway(EntityGateway):
    _entity = 'comment'

    def get_by_post(self, post_id, result_size=100, **kwargs):
        post = Post(id=post_id)
        comments = self.entity(post=post)
        r = self._filter(comments, page_opts={'size': result_size}, **kwargs)

        return make_entity(self._entity, r.json(), many=True)

    def new(self, content, post_id, user, access_token):
        post = Post(id=post_id)
        comment = self.entity(content=content, post=post, user=user)
        r = self._new(comment, access_token)

        return make_entity(self._entity, r.json())

    def delete(self, id, access_token):
        comment = self.entity(id=id)
        r = self._delete(comment, access_token)

        return r
