from os.path import join
from datetime import datetime
from io import BytesIO

import pytest
from flask import url_for, request
from flask_login import current_user

from benwaonline.models import Post, User, Comment, Preview, Image

RESP = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

FORM = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Lover', 'submit': True}

def authenticate(client, mocker, resp=RESP):
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    return client.get(url_for('auth.oauthorize_callback'), follow_redirects=False)

def signup(client, form=FORM, redirects=True):
    return client.post('/signup', data=form, follow_redirects=redirects)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def make_post(client):
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}
    test_post['image'] = (BytesIO(b'my file contents'), 'bartwa.jpg')
    return client.post('/gallery/benwa/add', content_type='multipart/form-data',
            data=test_post, follow_redirects=True)

def make_comment(client, post_id, data):
    uri = '/'.join(['/gallery/benwa', str(post_id), 'comment/add'])
    return client.post(uri, data=data)

def test_show_posts(client, session):
    response = client.get('/gallery')
    assert response.status_code == 301
    assert 'gallery' in response.headers['Location']

    response = client.get('/gallery/')
    assert response.status_code == 200

    response = client.get('/gallery/benwa')
    assert response.status_code == 301
    assert 'gallery/benwa' in response.headers['Location']

    response = client.get('/gallery/benwa oldbenwa', follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/gallery/benwa oldbenwa')
    assert response.status_code == 301
    assert 'gallery/benwa%20oldbenwa' in response.headers['Location']

def test_show_post_redirect(client, session):
    response = client.get('/gallery/show', follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/gallery/show', follow_redirects=False)
    assert response.status_code == 301
    assert 'gallery/' in response.headers['Location']

def test_show_post(client, session):
    response = client.get('/gallery/benwa/1', follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery/' in response.headers['Location']

    post = Post(title='test', created=datetime.utcnow())
    session.add(post)

    response = client.get('/gallery/benwa/1')
    assert response.status_code == 200

def test_add_post(client, session, mocker):
    # Set up post info
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}

    # Test trying to post while not logged in
    assert not current_user.is_authenticated
    response = client.post('/gallery/benwa/add', data=test_post, follow_redirects=False)
    assert 'login' in response.headers['Location']

    # Set up user
    authenticate(client, mocker)
    signup(client)

    assert current_user.is_authenticated

    # Add post
    make_post(client)

    post = Post.query.first()
    assert post
    assert current_user.id == post.user.id

    post_tags = [tag.name for tag in post.tags]
    for tag in test_post['tags']:
        assert tag in post_tags

# This may be too big for a unit test?
def test_add_comment(client, session, mocker):
    # Set up user
    authenticate(client, mocker)
    signup(client)
    make_post(client)

    # Set up comment
    comment = {'content': 'test comment', 'submit': True}
    make_comment(client, 1, comment)

    user = User.query.first()
    user_comment = user.comments.one()
    assert user_comment.content == comment['content']

    post = Post.query.first()
    post_comment = post.comments.one()
    assert post_comment.content == comment['content']

    comment = Comment.query.first()
    assert comment.user.username == user.username
    assert comment.post.id == post.id

# Test
# Deleting as admin
def test_delete_comment(client, session, mocker):
    authenticate(client, mocker)
    signup(client)
    make_post(client)
    comment = {'content': 'test comment', 'submit': True}
    make_comment(client, 1, comment)

    comment = Comment.query.first()
    comment_id = str(comment.id)
    uri = '/'.join(['/gallery/benwa/1/comment/delete', comment_id])
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