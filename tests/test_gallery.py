import datetime
from io import BytesIO
import requests
import requests_mock
import pytest
from marshmallow import pprint
import json

from flask import url_for, request, current_app
from flask_login import current_user

from benwaonline import schemas

payload = {
    "iss": "https://choosegoose.auth0.com/",
    "sub": "twitter|59866964",
    "aud": "1LX50Fa2L80jfr9P31aSZ5tifrnLFGDy",
    "iat": 1511860306,
    "exp": 1511896306
}

def authenticate(client, mocker):
    auth0_resp = {
        "access_token": "LnUwYsyKvQgo8dLOeC84y-fsv_F7bzvZ",
        "expires_in": 86400,
        'id_token': 'long',
        "scope": "openid email",
        "token_type": "Bearer"
    }

    jwks = {'yea': 'im a jwks'}

    mocker.patch('benwaonline.oauth.auth0.authorized_response', return_value=auth0_resp)
    mocker.patch('benwaonlineapi.util.get_jwks', return_value=jwks)
    return client.get(url_for('authbp.login_callback'), follow_redirects=False)

def signup(client, redirects=False):
    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Lover', 'submit': True}
    return client.post(url_for('authbp.signup'), data=form, follow_redirects=redirects)

def login(client, mocker):
    payload['sub'] = 'twitter|666'
    user = schemas.UserSchema().dump({
        'id': '1',
        "active": True,
        "created_on": datetime.datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Fan"
    }).data

    mocker.patch('benwaonline.auth.views.verify_token', return_value=payload)
    with requests_mock.Mocker() as mock:
        mock.get(current_app.config['API_URL'] + '/users', json=user)
        mock.get(current_app.config['JWKS_URL'], json={'data':[]})
        authenticate(client, mocker)

def logout(client):
    return client.get('/auth/logout/callback', follow_redirects=False)

def make_post(client, mocker):
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}
    test_post['image'] = (BytesIO(b'my file contents'), 'bartwa.jpg')
    mocker.patch('scripts.thumb.make_thumbnail', return_value=None)
    return client.post(url_for('gallery.add_post'), content_type='multipart/form-data',
            data=test_post, follow_redirects=True)

def make_comment(client, post_id, data):
    uri = url_for('gallery.add_comment', post_id=post_id)
    return client.post(uri, data=data)

def test_show_posts(client):
    # Show posts with empty db
    uri = current_app.config['API_URL']
    with requests_mock.Mocker() as mock:
        mock.get(uri + '/posts', json={'data':[]})
        mock.get(uri + '/tags', json={'data':[]})

        response = client.get(url_for('gallery.show_posts'))
        assert response.status_code == 200

        response = client.get(url_for('gallery.show_posts', tags='benwa'))
        assert response.status_code == 200

        response = client.get(url_for('gallery.show_posts', tags='benwa oldbenwa'), follow_redirects=True)
        assert response.status_code == 200

def test_show_post(client, mocker):
    # Test if post doesn't exist
    with requests_mock.Mocker() as mock:
        uri = current_app.config['API_URL'] + '/posts/69'
        mock.get(uri, status_code=404)
        response = client.get(url_for('gallery.show_post', post_id=69), follow_redirects=False)

        assert response.status_code == 302
        assert 'gallery/' in response.headers['Location']

    # Test if post exists
    with open('tests\\data\\postclient_get_single.json') as f:
        post = json.load(f)

    mocker.patch('benwaonline.gateways.PostGateway.get', return_value=post)
    response = client.get(url_for('gallery.show_post', post_id=69), follow_redirects=False)

    assert response.status_code == 200

@pytest.mark.skip
def test_add_post(client, dbsession, mocker):
    # Set up post info
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}

    # Test trying to post while not logged in
    assert not current_user.is_authenticated
    response = client.post('/gallery/add', data=test_post, follow_redirects=False)
    assert 'login' in response.headers['Location']

    # Set up user
    authenticate(client, mocker)
    signup(client)

    assert current_user.is_authenticated

    # Add post
    make_post(client, mocker)

    post = Post.query.first()
    assert post
    assert current_user.id == post.user.id

    post_tags = [tag.name for tag in post.tags]
    for tag in test_post['tags']:
        assert tag in post_tags

def test_add_comment(client, mocker):
    login(client, mocker)
    assert current_user.is_authenticated

@pytest.mark.skip
def test_delete_comment(client, mocker):
    login(client, mocker)
    assert current_user.is_authenticated

    