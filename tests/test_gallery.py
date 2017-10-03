from os.path import join
from datetime import datetime
from io import BytesIO
import pytest
from flask import url_for, current_app
from flask_login import current_user
from benwaonline.models import Post, User, Comment, Tag, Preview, Image

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

def test_add_post(client, session, testdir, mocker):
    # Set up tag
    tag = Tag(created=datetime.utcnow(), name='benwa')
    session.add(tag)
    session.commit()

    # Set up post info
    test_post = {'tags': ['old_benwa', 'benwa'], 'submit': True}

    # Test trying to post while not logged in
    assert not current_user.is_authenticated
    response = client.post('/gallery/benwa/add', data=test_post, follow_redirects=False)
    assert 'next' in response.headers['Location']

    # Set up mock oauth
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    client.get(url_for('auth.oauthorize_callback'), follow_redirects=False)

    # Set up user
    form = {'adj': 'beautiful', 'benwa': 'benwa', 'pos': 'lover', 'submit': True}
    client.post('/signup', data=form, follow_redirects=True)
    assert current_user.is_authenticated

    # Add post
    test_post['image'] = (BytesIO(b'my file contents'), 'bartwa.jpg')
    client.post('/gallery/benwa/add', content_type='multipart/form-data',
        data=test_post, follow_redirects=True)

    post = Post.query.first()
    assert post
    assert post.title == test_post['image'][1]
    assert current_user.id == post.user.id

    post_tags = [tag.name for tag in post.tags]
    for tag in test_post['tags']:
        assert tag in post_tags


# This may be too big for a unit test?
def test_add_comment(client, session, mocker):
    # Set up post
    preview = Preview(filepath='whocars')
    session.add(preview)
    image = Image(preview=preview, filepath='not rea')
    session.add(image)
    post = Post(title='test', created=datetime.utcnow(), image=image)
    session.add(post)

    # Set up mock oauth
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    client.get(url_for('auth.oauthorize_callback'), follow_redirects=False)

    # Set up user
    form = {'adj': 'beautiful', 'benwa': 'benwa', 'pos': 'lover', 'submit': True}
    client.post('/signup', data=form, follow_redirects=True)

    # Set up comment
    comment = {'content': 'test comment', 'submit': True}
    client.post('/gallery/benwa/1/comment/add', data=comment)

    user = User.query.first()
    user_comment = user.comments.one()
    assert user_comment.content == comment['content']

    post_comment = post.comments.one()
    assert post_comment.content == comment['content']

    comment = Comment.query.first()
    assert comment.user.username == user.username
    assert comment.post.id == post.id
