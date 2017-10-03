import pytest
from flask import url_for
from flask_login import current_user
from passlib.hash import bcrypt

from benwaonline.models import User, user_datastore
from benwaonline.oauth import twitter

# Create a user to test with
def create_user(client, session):
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    username = 'test'
    instance = user_datastore.create_user(user_id=resp['user_id'], username=username,\
            oauth_token_hash=resp['oauth_token'], oauth_secret_hash=resp['oauth_token_secret'])
    session.commit()

    return instance

def test_login_oauthorize(client):
    # tests the redirect from your application to the OAuth2 provider's "authorize" URL
    response = client.post('/login/auth')
    assert response.status_code == 302
    assert twitter.authorize_url in response.headers['Location']

def test_oauthorize_callback(client, mocker, session):
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    # Test where we received a response and user doesn't exist
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    response = client.get(url_for('auth.oauthorize_callback'), follow_redirects=False)
    assert response.status_code == 302
    assert 'signup' in response.headers['Location']

    # Test signup
    form = {'adj': 'beautiful', 'benwa': 'benwa', 'pos': 'lover', 'submit': True}
    response = client.post('/signup', data=form, follow_redirects=True)
    assert response.status_code == 200

    # Test to make sure the user made it to the database
    user = User.query.first()
    assert user.username == ''.join([form['adj'], form['benwa'], form['pos']])
    assert user.user_id == '420'
    assert user.verify_oauth_token(resp['oauth_token'])
    assert user.verify_oauth_secret(resp['oauth_token_secret'])

    with pytest.raises(AttributeError):
        user.oauth_token

    with pytest.raises(AttributeError):
        user.oauth_secret

    # Test where we receive a response and the user already exists
    response = client.get(url_for('auth.oauthorize_callback'), follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery' in response.headers['Location']

    # Test that we are logged in
    assert current_user.is_authenticated
    assert response.status_code == 302
    response = client.get(url_for('auth.oauthorize', follow_redirects=False))
    assert 'gallery' in response.headers['Location']

    # Checking signup handles an existing user correctly
    response = client.post('/signup', data=form, follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery' in response.headers['Location']

    # Test log out
    response = client.get(url_for('auth.logout'), follow_redirects=True)
    assert not current_user.is_authenticated
    assert response.status_code == 200
    client.get(url_for('gallery.show_posts'), follow_redirects=True)
    # Test where user denied / didnt receive a response
    resp = {}
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    response = client.get(url_for('auth.oauthorize_callback'), follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery' in response.headers['Location']
