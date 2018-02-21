from datetime import datetime
from io import BytesIO
# import requests
import requests_mock
import pytest
from jose import jwt
from marshmallow import pprint
import json

from flask import url_for, request, current_app
from flask_login import current_user

from benwaonline.schemas import UserSchema
from benwaonline.entities import Post

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

def test_show_posts(client):
    # Show posts with empty db
    uri = current_app.config['API_URL']
    with requests_mock.Mocker() as mock:
        mock.get(uri + '/api/posts', json={'data':[]})
        mock.get(uri + '/api/tags', json={'data':[]})
        response = client.get(url_for('gallery.show_posts'))
        assert response.status_code == 200

        response = client.get(url_for('gallery.show_posts', tags='benwa'))
        assert response.status_code == 200

        response = client.get(url_for('gallery.show_posts', tags='benwa+oldbenwa'), follow_redirects=True)
        assert response.status_code == 200

# This is getting pretty complicated
# Probably need a new set of tests for the gateways.py stuff
def test_show_post(client, mocker):
    # Test if post doesn't exist
    with requests_mock.Mocker() as mock:
        uri = current_app.config['API_URL'] + '/api/posts/69'
        mock.get(uri, status_code=404)
        response = client.get(url_for('gallery.show_post', post_id=69), follow_redirects=False)

        assert response.status_code == 302
        assert 'gallery/' in response.headers['Location']

        # Test if post exists
        with open('tests/data/postclient_get_single.json') as f:
            post = json.load(f)

        uri = current_app.config['API_URL']
        mock.get(requests_mock.ANY)
        mocker.patch('benwaonline.entities.Post.from_response', return_value=Post(**post))
        mocker.patch('benwaonline.entities.Comment.from_response', return_value=[])
        response = client.get(url_for('gallery.show_post', post_id=69), follow_redirects=False)

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

