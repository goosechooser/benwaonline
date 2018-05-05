from benwaonline.gateways import EntityGateway
from benwaonline import mappers, assemblers

class CommentGateway(EntityGateway):
    _entity = 'comment'

    def get_by_post(self, post_id, **kwargs):
        post = assemblers.get_entity('post')(id=post_id)
        comments = self.entity(post=post)
        r = self._filter(comments, **kwargs)

        return assemblers.make_entity(self._entity, r.json(), many=True)

    def new(self, content, post_id, user, access_token):
        post = assemblers.get_entity('post')(id=post_id)
        comment = self.entity(id=666, content=content, post=post, user=user)
        r = self._new(comment, access_token)

        return assemblers.make_entity(self._entity, r.json())

    def delete(self, comment_id, access_token):
        e = self.entity(id=comment_id)
        super().delete(e, access_token)
