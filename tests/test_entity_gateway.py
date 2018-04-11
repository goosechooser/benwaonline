import pytest
import requests_mock
from requests import Response
from requests.exceptions import HTTPError

from benwaonline import entities
from benwaonline.gateways import prepare_params
from benwaonline.entity_gateways import CommentGateway
from benwaonline.exceptions import BenwaOnlineRequestError

def errors(errors_):
    error_entries = [error.__dict__ for error in errors_]
    return {
        "errors": error_entries,
        "jsonapi": {
            "version": "1.0"
        }
    }

def test_prepare_params_include():
    test = {'include': ['nice', 'test']}
    params = prepare_params(**test)
    assert params['include'] == 'nice,test'

    params = prepare_params(include=['nice', 'test'])
    assert params['include'] == 'nice,test'

def test_relationship_uri():
    user = entities.User(id=1)
    expected = '/api/users/1/relationships/posts'
    assert user.relationship_uri('posts') == expected

def test_get_resource():
    user = entities.User(id=1)
    expected = '/api/users/1/posts'
    assert user.resource_uri('posts') == expected

def test_comment_gateway_new(client):
    user = entities.User(id=1)
    content='nice comment'
    post_id = 1

    with requests_mock.Mocker() as mock:
        mock.post('/api/comments', json=entities.Comment(content=content, id=69).dump())
        result = CommentGateway().new(content, post_id, user, 'token')

    assert isinstance(result, entities.Comment)

def test_comment_gateway_new_exception(client):
    user = entities.User(id=1)
    content = 'nice comment'
    post_id = 1

    error = BenwaOnlineRequestError(title='what an error', detail='idk')
    with requests_mock.Mocker() as mock:
        mock.post('/api/comments', status_code=404, json=errors([error]))
        with pytest.raises(BenwaOnlineRequestError):
            CommentGateway().new(content, post_id, user, 'token')

# Not sure which style I like better
# Is it purely aesthetics or is one better for testing??
class CommentGatewayStub(CommentGateway):
    def _new(self, comment, auth_token):
        comment.id = 69
        with requests_mock.Mocker() as mock:
            mock.post('/api/comments', status_code=200, json=comment.dump())
            return super()._new(comment, auth_token)

def test_comment_gateway_new_stub(client):
    user = entities.User(id=1)
    content = 'nice comment'
    post_id = 1

    result = CommentGatewayStub().new(content, post_id, user, 'token')

    assert isinstance(result, entities.Comment)
