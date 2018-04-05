from benwaonline import gateways as rf
from benwaonline import entities
from benwaonline.query import EntityQuery
from benwaonline.oauth import TokenAuth

from benwaonline.exceptions import BenwaOnlineRequestError
from requests.exceptions import HTTPError

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
    def _new(self, entity, access_token):
        auth = TokenAuth(access_token)
        return rf.post(entity, auth)

    def _delete(self, entity, access_token):
        auth = TokenAuth(access_token)
        return rf.delete(entity, auth)

    def _filter(self, entity):
        q = EntityQuery(entity)
        r = rf.filter(entity, q)
        entities = entity.from_response(r, many=True)
        return entities

    def _filter_single(self, entity):
        entities = self._filter(entity)
        try:
            return entities[0]
        except IndexError:
            return None

class CommentGateway(EntityGateway):
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
    def new(self, title, tags, image, preview, user, access_token):
        post = entities.Post(title=title, tags=tags, image=image, preview=preview, user=user)
        r = self._new(post, access_token)

        handle_response_error(r)

        return entities.Post.from_response(r)

class TagGateway(EntityGateway):
    def get_by_name(self, name):
        tag = entities.Tag(name=name)
        return self._filter_single(tag)

    def new(self, name, access_token):
        tag = entities.Tag(name=name)
        r = self._new(tag, access_token)

        handle_response_error(r)

        return tag.from_response(r)

class ImageGateway(EntityGateway):
    def new(self, filename, access_token):
        image = entities.Image(filepath=filename)
        r = self._new(image, access_token)

        handle_response_error(r)

        return image.from_response(r)

class PreviewGateway(EntityGateway):
    def new(self, filename, access_token):
        preview = entities.Preview(filepath=filename)
        r = self._new(preview, access_token)

        handle_response_error(r)

        return preview.from_response(r)