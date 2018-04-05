from benwaonline import gateways as rf
from benwaonline import entities
from benwaonline.query import EntityQuery
from benwaonline.oauth import TokenAuth

from benwaonline.exceptions import BenwaOnlineRequestError
from requests.exceptions import HTTPError

def single(entity):
    try:
        return entity[0]
    except IndexError:
        return None

def handle_response_error(response):
    '''JSONAPI can return an array of different errors.
    Not entirely sure what the best practice for dealing with this is.
    So we're gonna take the lazy route.
    '''
    try:
        response.raise_for_status()
    except HTTPError:
        errors = response.json()['errors']
        raise BenwaOnlineRequestError(errors[0])

class EntityGateway(object):
    def __init__(self, entity):
        self.entity = entity

    def get(self, include=None, result_size=100):
        entities = self.entity()
        r = self._get(entities, include, {'size': result_size})

        handle_response_error(r)

        return entities.from_response(r, many=True)

    def get_by_id(self, id, include=None):
        entity = self.entity(id=id)
        r = self._get_by_id(entity, include)

        handle_response_error(r)

        return entity.from_response(r)

    def _get(self, entity, include, page_opts):
        return rf.get(entity, include=include, page_opts=page_opts)

    def _get_by_id(self, entity, include):
        return rf.get_instance(entity, include)

    def _new(self, entity, access_token):
        auth = TokenAuth(access_token)
        return rf.post(entity, auth)

    def _delete(self, entity, access_token):
        auth = TokenAuth(access_token)
        return rf.delete(entity, auth)

    def _filter(self, entity, include, page_opts):
        q = EntityQuery(entity)
        return rf.filter(entity, q, include, page_opts)

class CommentGateway(EntityGateway):
    def __init__(self):
        super().__init__(entities.Comment)

    def get_by_post(self, post_id, include=None, result_size=100):
        post = entities.Post(id=post_id)
        comments = self.entity(post=post)
        r = self._filter(comments, include, {'size': result_size})

        handle_response_error(r)

        return self.entity.from_response(r, many=True)

    def new(self, content, post_id, user, access_token):
        post = entities.Post(id=post_id)
        comment = entities.Comment(content=content, post=post, user=user)
        r = self._new(comment, access_token)

        handle_response_error(r)

        return comment.from_response(r)

    def delete(self, comment_id, access_token):
        comment = entities.Comment(id=comment_id)
        r = self._delete(comment, access_token)

        handle_response_error(r)

        return r

class PostGateway(EntityGateway):
    def __init__(self):
        super().__init__(entities.Post)

    def new(self, title, tags, image, preview, user, access_token):
        post = entities.Post(title=title, tags=tags, image=image, preview=preview, user=user)
        r = self._new(post, access_token)

        handle_response_error(r)

        return entities.Post.from_response(r)

    def tagged_with(self, tag_names, include=None, result_size=100):
        '''Returns all Posts that are tagged with any of the given tags.'''
        tags = [entities.Tag(name=tag) for tag in tag_names]
        posts = entities.Post(tags=tags)

        r = self._filter(posts, include, {'size': result_size})

        handle_response_error(r)

        return posts.from_response(r, many=True)

class UserGateway(EntityGateway):
    def __init__(self):
        super().__init__(entities.User)

    def get_by_user_id(self, user_id):
        user = self.entity(user_id=user_id)
        r = self._filter(user, None, None)

        handle_response_error(r)

        return single(self.entity.from_response(r, many=True))

    def get_by_username(self, username):
        user = self.entity(username=username)
        r = self._filter(user, None, None)

        handle_response_error(r)

        return single(self.entity.from_response(r, many=True))

    def new(self, username, access_token):
        user = self.entity(username=username)
        r = self._new(user, access_token)

        handle_response_error(r)

        return user.from_response(r)

class TagGateway(EntityGateway):
    def __init__(self):
        super().__init__(entities.Tag)

    def get_by_name(self, name):
        tag = entities.Tag(name=name)
        r = self._filter(tag, None, None)

        handle_response_error(r)

        return single(tag.from_response(r, many=True))

    def new(self, name, access_token):
        tag = entities.Tag(name=name)
        r = self._new(tag, access_token)

        handle_response_error(r)

        return tag.from_response(r)

class ImageGateway(EntityGateway):
    def __init__(self):
        super().__init__(entities.Image)

    def new(self, filename, access_token):
        image = entities.Image(filepath=filename)
        r = self._new(image, access_token)

        handle_response_error(r)

        return image.from_response(r)

class PreviewGateway(EntityGateway):
    def __init__(self):
        super().__init__(entities.Preview)

    def new(self, filename, access_token):
        preview = entities.Preview(filepath=filename)
        r = self._new(preview, access_token)

        handle_response_error(r)

        return preview.from_response(r)