import datetime
from io import BytesIO
import requests
import requests_mock
import pytest
from marshmallow import pprint
import json

from flask import url_for, request, current_app
from flask_login import current_user
from benwaonline.gallery.base import create_tag

from benwaonlineapi import schemas

auth0_resp = {
  "access_token": "LnUwYsyKvQgo8dLOeC84y-fsv_F7bzvZ",
  "expires_in": 86400,
  'id_token': 'long',
  "scope": "openid email",
  "token_type": "Bearer"
}

payload = {
    "iss": "https://choosegoose.auth0.com/",
    "sub": "twitter|59866964",
    "aud": "1LX50Fa2L80jfr9P31aSZ5tifrnLFGDy",
    "iat": 1511860306,
    "exp": 1511896306
}

jwks = {'yea': 'im a jwks'}

def authenticate(client, mocker, resp):
    mocker.patch('benwaonline.oauth.auth0.authorized_response', return_value=resp)
    mocker.patch('benwaonline.auth.views.get_jwks', return_value=jwks)
    return client.get(url_for('authbp.login_callback'), follow_redirects=False)

def signup(client, redirects=False):
    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Lover', 'submit': True}
    return client.post(url_for('authbp.signup'), data=form, follow_redirects=redirects)

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

def test_create_tag():
    uri = current_app.config['API_URL'] + '/tags'
    with requests_mock.Mocker() as mock:
        mock.get(uri + '/benwa', status_code=404)
        mock.post(uri, status_code=201)
        r = requests.get(uri + '/benwa', hooks={'response': create_tag})

    assert r.status_code == 201

@pytest.mark.skip
def test_add_post(client, dbsession, mocker):
    # Set up post info
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}

    # Test trying to post while not logged in
    assert not current_user.is_authenticated
    response = client.post('/gallery/add', data=test_post, follow_redirects=False)
    assert 'login' in response.headers['Location']

    # Set up user
    authenticate(client, mocker, resp=auth0_resp)
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

@pytest.mark.skip
def test_add_comment(client, dbsession, mocker):
    authenticate(client, mocker, resp=auth0_resp)
    signup(client)
    assert current_user.is_authenticated

    comment = {'content': 'test comment', 'submit': True}
    make_comment(client, 1, comment)

    user = User.query.first()
    user_comment = user.comments.order_by('created_on desc').limit(1).first()
    assert user_comment.content == comment['content']

    post = Post.query.filter_by(id=user_comment.post_id)
    assert post

@pytest.mark.skip
def test_delete_comment(client, dbsession):
    # authenticate(client, mocker)
    # signup(client)
    # make_post(client)
    # comment = {'content': 'test comment', 'submit': True}
    # make_comment(client, 1, comment)

    # Test user deleting own comment
    user = User.query.first()
    user_id = user.id
    comment = user.comments[0]
    comment_id = str(comment.id)

    uri = url_for('gallery.delete_comment', comment_id=comment_id)
    response = client.get(uri)

    post = Post.query.first()
    assert len(post.comments.all()) == 0
    assert url_for('gallery.show_post', post_id=post.id) in request.path

    # Test someone attempting to delete a comment that isn't theres
    comment = {'content': 'test comment', 'submit': True}
    make_comment(client, 1, comment)
    logout(client)

    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '69', 'oauth_token': '59866969-token', 'screen_name': 'tester'}
    authenticate(client, mocker, resp=resp)

    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Game Dave', 'submit': True}
    signup(client, form)

    comment = Comment.query.first()
    comment_id = str(comment.id)
    uri = '/'.join(['/gallery/benwa/1/comment/delete', comment_id])
    response = client.get(uri)

    post = Post.query.first()
    assert len(post.comments.all()) == 1
    assert url_for('gallery.show_post', post_id=post.id) in request.path