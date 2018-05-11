import pytest
import requests_mock
from requests import Response
from requests.exceptions import HTTPError

from benwaonline import entities
from benwaonline.entities import Tag
from benwaonline.gateways import CommentGateway, TagGateway, PostGateway
from benwaonline.exceptions import BenwaOnlineRequestError
import utils

test_data = utils.load_test_data('show_comments.json')

def comments_previews():
    return test_data['comments_with_previews']

def tags_data():
    return utils.load_test_data('show_tags.json')

def test_tag_gateway_get():
    with requests_mock.Mocker() as mock:
        mock.get('/api/tags', json=tags_data())
        tags = TagGateway().get()

    assert len(tags) == tags_data()['meta']['count']

def test_tag_gateway_get_by_name():
    with requests_mock.Mocker() as mock:
        mock.get('/api/tags', json=tags_data())
        tag = TagGateway().get_by_name('benwa')

    assert isinstance(tag, Tag)
    assert tag.name == 'benwa'

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
        mock.post('/api/comments', status_code=404, json=utils.errors([error]))
        with pytest.raises(BenwaOnlineRequestError):
            CommentGateway().new(content, post_id, user, 'token')

def test_comment_gateway_includes(client):
    include = ['post.preview', 'user']
    with requests_mock.Mocker() as mock:
        mock.get('/api/comments', json=comments_previews())
        comments = CommentGateway().get(include=include)

    for c in comments:
        assert c.post.preview
        assert c.user

# Not sure which style I like better
# Is it purely aesthetics or is one better for testing??
class CommentGatewayStub(CommentGateway):
    def _new(self, comment, auth_token):
        comment.id = 69
        with requests_mock.Mocker() as mock:
            mock.post('/api/comments', status_code=200, json=comment.dump())
            return super()._new(comment, auth_token)

@pytest.mark.skip
def test_comment_gateway_new_stub(client):
    user = entities.User(id=1)
    content = 'nice comment'
    post_id = 1

    result = CommentGatewayStub().new(content, post_id, user, 'token')

    assert isinstance(result, entities.Comment)

class PostGatewayStub(PostGateway):
    results = None
    def _post(self, uri, data, auth, params=None):
        self.results = {
            'uri': uri,
            'data': data,
            'auth': auth,
            'params': params
        }
        return

# Figure out where the f to patch, or perish,,
@pytest.mark.skip
def test_post_gateway_new(mocker):
    mock = mocker.patch('benwaonline.gateways.PostGateway')
    mock.return_value.make_entity.return_value = True
    stub = PostGatewayStub()
    stub.new('access', title='helo', tags=[Tag(id=1)])
    print(stub.results)

    assert False
