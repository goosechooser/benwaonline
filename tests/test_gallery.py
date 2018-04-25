import sys
import json
from datetime import datetime
from io import BytesIO

import pytest
import requests_mock
from flask import current_app, request, url_for
from flask_login import current_user
from marshmallow import pprint

from benwaonline import mappers
from benwaonline import entities
from benwaonline.gallery import views
from benwaonline.exceptions import BenwaOnlineError, BenwaOnlineRequestError
import utils

JWKS = utils.load_test_data('test_jwks.json')

def benwa_resp():
    return {
        "access_token": "LnUwYsyKvQgo8dLOeC84y-fsv_F7bzvZ",
        'refresh_token': 'refresh_me_thanks',
        "expires_in": 3600,
        "scope": "openid email",
        "token_type": "Bearer"
    }

def auth_payload():
    return {
        "iss": "https://choosegoose.benwa.com/",
        "sub": "59866964",
        "aud": "1LX50Fa2L80jfr9P31aSZ5tifrnLFGDy",
        "iat": 1511860306,
        "exp": 1511896306
    }

def mock_auth_response(mocker, resp):
    mock = mocker.patch('benwaonline.auth.views.benwa.authorized_response')
    mock.return_value = resp
    return mock

def login(client, mocker, m):
    user = utils.test_user()
    mocker.patch('benwaonline.auth.views.get_jwks', return_value=JWKS)
    mocker.patch('benwaonline.auth.views.verify_token', return_value=auth_payload())
    mocker.patch('benwaonline.auth.views.handle_authorize_response', return_value=benwa_resp())
    mocker.patch('benwaonline.auth.views.UserGateway.get_by_user_id', return_value=user)
    return client.get(url_for('authbp.authorize_callback'), follow_redirects=False)

def signup(client, redirects=False):
    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Aficionado', 'submit': True}
    return client.post(url_for('authbp.signup'), data=form, follow_redirects=redirects)

def logout(client):
    mocker.patch('benwaonline.auth.views.verify_token', return_value=auth_payload())
    return client.get('/auth/logout/callback', follow_redirects=False)

def make_comment(client, post_id, data):
    uri = url_for('gallery.add_comment', post_id=post_id)
    return client.post(uri, data=data)

class TestShowPosts(object):
    post_uri = mappers.collection_uri(entities.Post())
    tag_uri = mappers.collection_uri(entities.Tag())

    with open('tests/data/show_posts.json') as f:
        test_data = json.load(f)

    def test_empty_db(self, client):
        with requests_mock.Mocker() as mock:
            mock.get('/api/posts', json={'data': []})
            mock.get(self.tag_uri, json={'data':[]})

            response = client.get(url_for('gallery.show_posts'))
            assert response.status_code == 200

            response = client.get(url_for('gallery.show_posts', tags='benwa'))
            assert response.status_code == 200

            response = client.get(url_for('gallery.show_posts', tags='benwa+oldbenwa'), follow_redirects=True)
            assert response.status_code == 200

    def test_posts_exist(self, client):
        posts = self.test_data['posts_with_previews']
        tags = self.test_data['tags']
        with requests_mock.Mocker() as mock:
            mock.get('/api/posts', json=posts)
            mock.get(self.tag_uri, json=tags)

            response = client.get(url_for('gallery.show_posts'))
            assert response.status_code == 200

            response = client.get(url_for('gallery.show_posts', tags='benwa'))
            assert response.status_code == 200

            response = client.get(
                url_for('gallery.show_posts', tags='benwa+oldbenwa'), follow_redirects=True)
            assert response.status_code == 200

class TestShowPost(object):
    post_id = 1
    post_uri = mappers.instance_uri(entities.Post(id=1))
    comments_uri = mappers.resource_uri(entities.Post(id=1), 'comments')

    with open('tests/data/show_post.json') as f:
        test_data = json.load(f)

    post = test_data['post']
    comments = test_data['comments']

    def test_no_post_exists(self, client, mocker):
        with requests_mock.Mocker() as mock:
            mock.get(self.post_uri, status_code=404, json=utils.error_response('Post', 1))
            response = client.get(
                url_for('gallery.show_post', post_id=self.post_id), follow_redirects=False)
            assert response.status_code == 200

            with pytest.raises(BenwaOnlineRequestError):
                template = views.show_post(post_id=1)
                assert 'Object not found' in template

    def test_post_exists_no_comments(self, client, mocker):
        with requests_mock.Mocker() as mock:
            mock.get(self.post_uri, json=self.post)
            mock.get('/api/posts/1/comments', json={'data':[]})
            response = client.get(url_for('gallery.show_post', post_id=self.post_id), follow_redirects=False)
            assert response.status_code == 200

    def test_post_exists_comments(self, client, mocker):
        self.post = self.test_data['post_comments_exist']
        with requests_mock.Mocker() as mock:
            mock.get(self.post_uri, json=self.post)
            mock.get('/api/posts/1/comments', json=self.comments)
            response = client.get(url_for('gallery.show_post', post_id=self.post_id), follow_redirects=False)
            assert response.status_code == 200

def test_add_post_not_authenticated(client):
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}
    assert not current_user.is_authenticated

    response = client.get('/gallery/add', follow_redirects=False)
    assert 'authorize' in response.headers['Location']

    response = client.post('/gallery/add', data=test_post, follow_redirects=False)
    assert 'authorize' in response.headers['Location']

def test_add_post_not_valid_submit(client, mocker):
    test_post = {
        'tags': ['old_benwa', 'benwa'],
        'filename': 'bartwa.jpg',
        'submit': True
        }
    with requests_mock.Mocker() as mock:
        login(client, mocker, mock)
        response = client.post(url_for('gallery.add_post'), content_type='multipart/form-data',
                    data=test_post, follow_redirects=False)

    assert response.status_code == 200

def test_add_post(client, mocker):
    test_post = {
        'tags': ['old_benwa', 'benwa'],
        'filename': 'bartwa.jpg',
        'image': (BytesIO(b'my file contents'), 'bartwa.jpg'),
        'submit': True
        }

    mocker.patch.object(sys.modules['benwaonline.gallery.views'], 'make_thumbnail')
    mocker.patch.object(sys.modules['benwaonline.gallery.views'], 'save_image')
    user = utils.test_user().dump()
    preview = entities.Preview(id=1)
    image = entities.Image(id=1)
    benwa_tag = entities.Tag(id=1, name='benwa')
    tag = entities.Tag(id=2, name='old_benwa')
    post = entities.Post(id=1, image=image, preview=preview, user=user, tags=[tag, benwa_tag])

    with requests_mock.Mocker() as mock:
        login(client, mocker, mock)

        mock.post('/api/previews', json=preview.dump())
        mock.post('/api/images', json=image.dump())
        mock.post('/api/posts', json=post.dump())
        mock.get('/api/posts/1', json=post.dump())
        mock.get('/api/tags', json={'data':[]})
        mock.post('/api/tags', json=tag.dump())
        response = client.post(url_for('gallery.add_post'), content_type='multipart/form-data',
                data=test_post, follow_redirects=False)

    assert response.status_code == 302
    assert 'gallery/show' in response.headers['Location']

@pytest.mark.skip
def test_add_comment(client, mocker):
    form = {'content': 'its valid man','submit': True}
    with client.session_transaction() as sess:
        sess['access_token'] = 'Bearer ' + 'access token'

    with requests_mock.Mocker() as mock:
        login(client, mocker, mock)
        mock.post(current_app.config['API_URL'] + '/comments')
        response = client.post(url_for('gallery.add_comment', post_id=1), data=form)


@pytest.mark.skip
def test_delete_comment(client, mocker):
    login(client, mocker)
    assert current_user.is_authenticated
