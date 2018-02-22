from datetime import datetime
import pytest
import jose
import requests_mock

from flask import url_for, request, current_app
from flask_login import current_user
from benwaonline.schemas import UserSchema
from tests.helpers.utils import error_response

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

jwks = {'yea': 'im a jwks'}

def authenticate(client, mocker, resp):
    mocker.patch('benwaonline.auth.views.benwa.authorized_response', return_value=resp)
    mocker.patch('benwaonline.auth.views.get_jwks', return_value=jwks)
    return client.get(url_for('authbp.authorize_callback'), follow_redirects=False)

def signup(client, redirects=False):
    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Aficionado', 'submit': True}
    return client.post(url_for('authbp.signup'), data=form, follow_redirects=redirects)

def logout(client):
    return client.get('/auth/logout/callback', follow_redirects=False)

def test_authorize_callback(client, mocker):
    # Test response was received, auth is valid, user doesn't exist
    uri = current_app.config['API_URL'] + '/api/users'

    payload['sub'] = '59866969'
    mocker.patch('benwaonline.auth.views.verify_token', return_value=payload)
    with requests_mock.Mocker() as mock:
        mock.get(uri, json={'data':[]}, status_code=404)
        response = authenticate(client, mocker, benwa_resp)

    assert response.status_code == 302
    assert url_for('authbp.signup') in response.headers['location']

    # Test where we received a response and the user exists, we log in
    payload['sub'] = '666'
    user = UserSchema(many=True).dump([{
        'id': '1',
        "active": True,
        "created_on": datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Fan"
    }]).data

    mocker.patch('benwaonline.auth.views.verify_token', return_value=payload)
    with requests_mock.Mocker() as mock:
        mock.get(uri, json=user)
        response = authenticate(client, mocker, benwa_resp)

    assert response.status_code == 302

    # Test that we are logged in
    assert current_user.is_authenticated
    assert 'gallery' in response.headers['location']

    # Test log out
    logout(client)
    assert response.status_code == 302

    # Test where user denied / didnt receive a response
    response = authenticate(client, mocker, None)
    assert response.status_code == 400

# @pytest.mark.skip
def test_signup(client, mocker):
    # Test GET request
    response = client.get(url_for('authbp.signup'), follow_redirects=False)
    assert response.status_code == 200
    assert 'signup' in request.path

    # Test POST request - username doesn't exist
    with client.session_transaction() as sess:
        # sess['profile'] = {'user_id': '59866965'}
        sess['access_token'] = 'Bearer ' + 'access token'

    uri = current_app.config['API_URL'] + '/api/users'

    user = UserSchema().dump({
        'id': '1',
        "active": True,
        "created_on": datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Fan"
    }).data
    with requests_mock.Mocker() as mock:
        mock.get(uri, json=error_response('User', 1), status_code=404)
        mock.post(uri, json=user, status_code=201)
        resp = signup(client)

    assert resp.status_code == 302
    assert current_user.is_authenticated

    # Logout before next test
    logout(client)
    # assert not current_user.is_authenticated

    # Test POST request - username already exists
    with requests_mock.Mocker() as mock:
        mock.get(uri, json=user, status_code=200)
        mock.get(uri + '/1', status_code=200)
        mocker.patch('benwaonline.entities.User.from_response', return_value='anything')
        resp = signup(client)

    assert 'signup' in request.path
