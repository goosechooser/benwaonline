import pytest
from flask import url_for, request
from flask_security import current_user

from benwaonline.models import User, user_datastore
from benwaonline.oauth import twitter
from benwaonline.auth.views import create_user

RESP = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

def authenticate(client, mocker, resp=RESP):
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    return client.get(url_for('auth.oauthorize_callback'), follow_redirects=False)

def signup(client, redirects=True):
    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Lover', 'submit': True}
    return client.post('/signup', data=form, follow_redirects=redirects)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_oauthorize(client, session, mocker):
    # Test GET request
    response = client.get(url_for('auth.oauthorize'), follow_redirects=False)
    assert response.status_code == 200
    assert url_for('auth.oauthorize') in request.path

    # tests the redirect from your application to the OAuth2 provider's "authorize" URL
    response = client.post(url_for('auth.oauthorize'))
    assert response.status_code == 302
    assert twitter.authorize_url in response.headers['Location']

    # Test user is authenticated already
    authenticate(client, mocker)
    signup(client)

    response = client.post(url_for('auth.oauthorize'), follow_redirects=False)
    assert response.status_code == 302
    assert url_for('gallery.show_posts') in response.headers['Location']

def test_oauthorize_callback(client, mocker, session):
    response = authenticate(client, mocker)
    assert response.status_code == 302
    assert 'signup' in response.headers['Location']

    # Test where we received a response and the user exists, we log in
    user_datastore.create_user(user_id='420', username='testbenwa')
    session.commit()

    response = authenticate(client, mocker)
    assert response.status_code == 302
    assert 'gallery' in response.headers['Location']

    # Test that we are logged in
    assert current_user.is_authenticated
    assert response.status_code == 302

    # Test log out
    logout(client)
    assert not current_user.is_authenticated
    assert response.status_code == 302

    # Test where user denied / didnt receive a response
    client.get(url_for('gallery.show_posts'), follow_redirects=True)
    resp = {}
    response = authenticate(client, mocker, resp)
    assert response.status_code == 302
    assert 'gallery' in response.headers['Location']

def test_signup(client, session, mocker):
    # Test GET request
    response = client.get('/signup', follow_redirects=False)
    assert response.status_code == 200
    assert 'signup' in request.path

    # Test POST request
    response = client.post('/signup', follow_redirects=False)
    assert response.status_code == 200
    assert 'signup' in request.path

    authenticate(client, mocker)
    response = signup(client, False)
    assert response.status_code == 302
    assert 'gallery' in response.headers['location']

    # Test already authenticated user
    assert current_user.is_authenticated
    response = signup(client, False)
    assert response.status_code == 302
    assert 'gallery' in response.headers['location']

def test_create_user(session):
    user_id = '420'
    adjective = 'Fantastic'
    noun = 'Test'
    token = 'cool'
    secret = 'sssh'

    # Test new user creation
    user = create_user(user_id, adjective, noun, token, secret)
    assert user

     # Test to make sure the user made it to the database
    user = User.query.first()
    assert user
    assert user.user_id == user_id

    # Test username already exists
    response = create_user(user_id, adjective, noun, None, None)
    assert 'signup' in response.headers['Location']