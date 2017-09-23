import pytest
from flask import g, url_for
from passlib.hash import bcrypt
from benwaonline.models import User, user_datastore
from benwaonline.oauth import twitter
from benwaonline.blueprints.benwaonline import get_or_create_user

# Create a user to test with
def create_user(client, session):
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    username = 'test'
    instance = user_datastore.create_user(user_id=resp['user_id'], username=username,\
            oauth_token_hash=resp['oauth_token'], oauth_secret_hash=resp['oauth_token_secret'])
    session.commit()

    return instance

def test_login_auth(client):
    # tests the redirect from your application to the OAuth2 provider's "authorize" URL
    response = client.get('/login/auth')
    assert response.status_code == 302
    assert twitter.authorize_url in response.headers['Location']

def test_oauthorized(client, mocker, session):
    from flask_login import current_user
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    # Test where we received a response
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    response = client.get(url_for('benwaonline.oauthorized'), follow_redirects=False)
    assert response.status_code == 302
    assert 'signup' in response.headers['Location']

    # Test where we receive a response and the user already exists
    test_user = create_user(client, session)
    response = client.get(url_for('benwaonline.oauthorized'), follow_redirects=False)
    assert response.status_code == 302
    assert 'test' in response.headers['Location']

    # Test that we are logged in
    assert current_user.is_authenticated

    # Test log out
    response = client.get(url_for('benwaonline.logout'), follow_redirects=True)
    assert not current_user.is_authenticated
    assert response.status_code == 200

    # Test where user denied / didnt receive a response
    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=None)
    response = client.get(url_for('benwaonline.oauthorized'), follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery' in response.headers['Location']

def test_get_or_create_user(client, session):
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
    test_user = create_user(client, session)
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
