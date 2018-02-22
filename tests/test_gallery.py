import json
from datetime import datetime
from io import BytesIO

import pytest
# import requests
import requests_mock
from flask import current_app, request, url_for
from flask_login import current_user
from jose import jwt
from marshmallow import pprint

from benwaonline.entities import Post, Tag, Comment
from benwaonline.schemas import UserSchema
from benwaonline.gallery import views
from benwaonline.exceptions import BenwaOnlineError, BenwaOnlineRequestError
from tests.helpers.utils import error_response

benwa_resp = {
  "access_token": "LnUwYsyKvQgo8dLOeC84y-fsv_F7bzvZ",
  'refresh_token': 'refresh_me_thanks',
  "expires_in": 3600,
  "scope": "openid email",
  "token_type": "Bearer"
}

payload = {
    "iss": "https://choosegoose.benwa.com/",
    "sub": "twitter|59866964",
    "aud": "1LX50Fa2L80jfr9P31aSZ5tifrnLFGDy",
    "iat": 1511860306,
    "exp": 1511896306
}

with open('tests/data/test_jwks.json', 'r') as f:
    JWKS = json.load(f)

def authenticate(client, mocker, resp):
    mocker.patch('benwaonline.auth.views.benwa.authorized_response', return_value=resp)
    mocker.patch('benwaonline.auth.views.get_jwks', return_value=JWKS)
    return client.get(url_for('authbp.authorize_callback'), follow_redirects=False)

def signup(client, redirects=False):
    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Lover', 'submit': True}
    return client.post(url_for('authbp.signup'), data=form, follow_redirects=redirects)

def login(client, mocker):
    payload['sub'] = '666'
    user = UserSchema().dump({
        'id': '1',
        "active": True,
        "created_on": datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Fan"
    }).data

    uri = current_app.config['API_URL'] + '/api/users'
    mocker.patch('benwaonline.auth.views.verify_token', return_value=payload)
    with requests_mock.Mocker() as mock:
        mock.get(uri, json=user)
        response = authenticate(client, mocker, benwa_resp)

def logout(client):
    return client.get('/auth/logout/callback', follow_redirects=False)

def make_comment(client, post_id, data):
    uri = url_for('gallery.add_comment', post_id=post_id)
    return client.post(uri, data=data)

class TestShowPosts(object):
    post_uri = Post().api_endpoint
    tag_uri = Tag().api_endpoint

    with open('tests/data/show_posts.json') as f:
        test_data = json.load(f)

    def test_empty_db(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.post_uri, json={'data': []})
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
            mock.get(self.post_uri, json=posts)
            mock.get(self.tag_uri, json=tags)

            response = client.get(url_for('gallery.show_posts'))
            assert response.status_code == 200

            response = client.get(url_for('gallery.show_posts', tags='benwa'))
            assert response.status_code == 200

            response = client.get(
                url_for('gallery.show_posts', tags='benwa+oldbenwa'), follow_redirects=True)
            assert response.status_code == 200

class TestShowPost(object):
    post_uri = Post(id=1).instance_uri
    comments_uri = Post(id=1).resource_uri(Comment())

    with open('tests/data/show_post.json') as f:
        test_data = json.load(f)

    post = test_data['post']
    comments = test_data['comments']

    def test_no_post_exists(self, client, mocker):
        with requests_mock.Mocker() as mock:
            mock.get(self.post_uri, status_code=404, json=error_response('Post', 1))
            response = client.get(
                url_for('gallery.show_post', post_id=1), follow_redirects=False)
            assert response.status_code == 200

            with pytest.raises(BenwaOnlineRequestError):
                template = views.show_post(post_id=1)
                assert 'Object not found' in template

    def test_post_exists_no_comments(self, client, mocker):
        with requests_mock.Mocker() as mock:
            mock.get(self.post_uri, json=self.post)
            response = client.get(url_for('gallery.show_post', post_id=1), follow_redirects=False)
            assert response.status_code == 200

    def test_post_exists_comments(self, client, mocker):
        self.post = self.test_data['post_comments_exist']
        with requests_mock.Mocker() as mock:
            mock.get(self.post_uri, json=self.post)
            mock.get(self.comments_uri, json=self.comments)
            response = client.get(url_for('gallery.show_post', post_id=1), follow_redirects=False)
            assert response.status_code == 200


# All these mocks, is this even a real test anymore
# Actually need to test this by testing all the request calls individually
# Trying to mock the make_thumbnail function will also require me to change
# The blueprint name zzzz
@pytest.mark.skip
def test_add_post(client, mocker):
    # Set up post info
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}

    # Test trying to post while not logged in
    assert not current_user.is_authenticated
    response = client.post('/gallery/add', data=test_post, follow_redirects=False)
    assert 'authorize' in response.headers['Location']

    login(client, mocker)
    assert current_user.is_authenticated

    # Add post
    # make_post(client, mocker)
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}
    test_post['image'] = (BytesIO(b'my file contents'), 'bartwa.jpg')
    # mocker.patch('scripts.thumb.make_thumbnail', return_value=None)
    mocker.patch('benwaonline.gallery.make_thumbnail', return_value=None)

    user = UserSchema().dump({
        'id': '1',
        "active": True,
        "created_on": datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Fan"
    }).data

    uri = current_app.config['API_URL'] + '/users/1'
    mocker.patch('benwaonline.auth.views.verify_token', return_value=payload)

    with requests_mock.Mocker() as mock:
        mock.get(uri, json=user)
        mock.post(current_app.config['API_URL'] + '/previews')
        mock.post(current_app.config['API_URL'] + '/images')
        mock.post(current_app.config['API_URL'] + '/posts')
        mock.post(current_app.config['API_URL'] + '/tags')
        mock.patch(current_app.config['API_URL'] + '/posts')
        client.post(url_for('gallery.add_post'), content_type='multipart/form-data',
                data=test_post, follow_redirects=True)

    assert False

@pytest.mark.skip
def test_add_comment(client, mocker):
    login(client, mocker)
    assert current_user.is_authenticated

@pytest.mark.skip
def test_delete_comment(client, mocker):
    login(client, mocker)
    assert current_user.is_authenticated
