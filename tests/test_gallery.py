from datetime import datetime
import pytest
from flask import url_for
from benwaonline.models import Post, User

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
    response = client.get('/gallery/show/1', follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery/' in response.headers['Location']

    post = Post(title='test', created=datetime.utcnow())
    session.add(post)

    response = client.get('/gallery/show/1')
    assert response.status_code == 200

# This may be too big for a unit test?
def test_add_comment(client, session, mocker):
    # Set up post
    post = Post(title='test', created=datetime.utcnow())
    session.add(post)

    # Set up mock oauth
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    client.get(url_for('benwaonline.oauthorize'), follow_redirects=False)

    # Set up user
    form = {'adj': 'beautiful', 'benwa': 'benwa', 'pos': 'lover', 'submit': True}
    client.post('/signup', data=form, follow_redirects=True)

    # Set up comment
    comment = {'content': 'test comment'}
    client.post('/gallery/show/1/add', data=comment)

    user = User.query.first()
    user_comment = user.comments.one()
    assert user_comment.content == 'test comment'

    post_comment = post.comments.one()
    assert post_comment.content == 'test comment'

    assert user_comment == post_comment
