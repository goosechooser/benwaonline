from benwaonline.entities import Comment, Post
from .base import EntityGateway

class CommentGateway(EntityGateway):
    def __init__(self):
        super().__init__(Comment)

    def get_by_post(self, post_id, result_size=100, **kwargs):
        post = Post(id=post_id)
        comments = self.entity(post=post)
        r = self._filter(comments, page_opts={'size': result_size}, **kwargs)

        return self.entity.from_response(r, many=True)

    def new(self, content, post_id, user, access_token):
        post = Post(id=post_id)
        comment = self.entity(content=content, post=post, user=user)
        r = self._new(comment, access_token)

        return comment.from_response(r)

    def delete(self, id, access_token):
        comment = self.entity(id=id)
        r = self._delete(comment, access_token)

        return r
