import pytest

from flask import g, url_for
from passlib.hash import bcrypt
from benwaonline.models import *
from benwaonline.oauth import twitter
from benwaonline.blueprints.benwaonline import get_or_create_user
from benwaonline.forms import RegistrationForm
# from scripts.add_benwas import add_post, add_posts

# Create a user to test with
def create_user(client, session):
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    username = 'test'
    instance = user_datastore.create_user(user_id=resp['user_id'], username=username,\
            oauth_token_hash=resp['oauth_token'], oauth_secret_hash=resp['oauth_token_secret'])
    session.commit()

    return instance

def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_login_auth(client):
    # tests the redirect from your application to the OAuth2 provider's "authorize" URL
    response = client.get('/login/auth')
    assert response.status_code == 302
    assert twitter.authorize_url in response.headers['Location']

def test_oauthorized(client, mocker, session):
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    # Test where we received a response
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    response = client.get(url_for('benwaonline.oauthorized'), follow_redirects=False)
    assert response.status_code == 302
    assert 'signup' in response.headers['Location']

    # Test where user denied / didnt receive a response
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=None)
    response = client.get(url_for('benwaonline.oauthorized'), follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery' in response.headers['Location']

def test_get_or_create_user(app, client, session):
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'super',
        'user_id': '420', 'oauth_token': '59866969-token',
        'screen_name': 'tester'}

    # Its a new user
    user, new = get_or_create_user(resp)
    assert not user
    assert new
    assert g.session['user_id'] == resp['user_id']
    assert bcrypt.verify(resp['oauth_token'], g.session['token'])
    assert bcrypt.verify(resp['oauth_token_secret'], g.session['secret'])

    # Its not a new user
    test_user = create_user(app, session)
    user, new = get_or_create_user(resp)
    assert not new
    assert user == test_user

def test_signup(client, app, session):
    # Test POST - do we get redirected?
    response = client.get(url_for('benwaonline.signup'), follow_redirects=False)
    assert response.status_code == 200
    assert b'<form action="" method="post" name="RegistrationForm"' in response.data

    # Test POST with fields
    form = {'adj': 'beautiful', 'benwa': 'benwa', 'pos': 'liker', 'submit': True}
    mock_oauth_response = {'x_auth_expires': '0', 'oauth_token_secret': 'super',
        'user_id': '420', 'oauth_token': '59866969-token',
        'screen_name': 'tester'}

    get_or_create_user(mock_oauth_response)
    response = client.post('/signup', data=form, follow_redirects=False)

    # Test that we were redirected to the right place
    assert response.status_code == 302
    assert 'test' in response.headers['Location']

    # Test to make sure the user made it to the database
    query = User.query.first()
    assert query.username == ''.join([form['adj'], form['benwa'], form['pos']])
    assert query.user_id == '420'



# def test_add_post(client, session):
#     img_path = 'benwaonline/static/benwas/test.png'
#     preview_path = 'benwaonline/static/benwas/preview.png'
#     add_post(img_path, preview_path)

#     post = Post.query.first()

#     # Dog I hate paths
#     # assert post.image.filepath == os.path.relpath(img_path, 'benwaonline/static/')
#     # assert post.preview.filepath == preview_path
#     # Figure out better way to check if List of tags contains name of
#     assert post.tags[0].name == 'benwa'

# def test_add_posts(session):
#     img_path = 'benwaonline/static/benwas/imgs'
#     preview_path = 'benwaonline/static/benwas/thumbs'
#     add_posts(img_path, preview_path)

#     posts = Post.query.all()
#     for post in posts:
#         print(post.tags.count)
#         _, img_tail = os.path.split(post.image.filepath)
#         print(img_tail)
#         _, preview_tail = os.path.split(post.preview.filepath)
#         print(preview_tail)

#         assert img_tail == preview_tail
#         # assert post.preview.filepath == preview_path
#         assert post.tags[0].name == 'benwa'