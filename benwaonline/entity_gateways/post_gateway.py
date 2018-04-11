from benwaonline.entities import Post, Tag
from .base import EntityGateway

class PostGateway(EntityGateway):
    def __init__(self):
        super().__init__(Post)

    def new(self, access_token, **kwargs):
        post = self.entity(**kwargs)
        r = self._new(post, access_token)

        return Post.from_response(r)

    def tagged_with(self, tag_names, result_size=100, **kwargs):
        '''Returns all Posts that are tagged with any of the given tags.'''
        tags = [Tag(name=tag) for tag in tag_names]
        posts = self.entity(tags=tags)
        r = self._filter(posts, page_opts={'size': result_size}, **kwargs)

        return posts.from_response(r, many=True)
