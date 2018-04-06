from datetime import datetime
import pytest
import jose
import requests_mock

from flask import url_for, request, current_app
from flask_login import current_user
from benwaonline.schemas import UserSchema
from benwaonline.entities import User
from benwaonline.auth.views import handle_authorize_response
import utils

def benwa_resp():
    return {
        "access_token": "LnUwYsyKvQgo8dLOeC84y-fsv_F7bzvZ",
        'refresh_token': 'refresh_me_thanks',
        "expires_in": 3600,
        "scope": "openid email",
        "token_type": "Bearer"
    }

def auth_payload():
    return {
        "iss": "https://choosegoose.benwa.com/",
        "sub": "59866964",
        "aud": "1LX50Fa2L80jfr9P31aSZ5tifrnLFGDy",
        "iat": 1511860306,
        "exp": 1511896306
    }

JWKS = {'yea': 'im a jwks'}

def test_user():
    return {
        'id': '1',
        "active": True,
        "created_on": datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Aficionado"
    }

def mock_auth_response(mocker, resp):
    mock = mocker.patch('benwaonline.auth.views.benwa.authorized_response')
    mock.return_value = resp
    return mock

def authenticate(client, mocker):
    mocker.patch('benwaonline.auth.views.get_jwks', return_value=JWKS)
    return client.get(url_for('authbp.authorize_callback'), follow_redirects=False)

def signup(client, access_token, redirects=False):
    with client.session_transaction() as sess:
        sess['access_token'] = access_token

    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Aficionado', 'submit': True}
    return client.post(url_for('authbp.signup'), data=form, follow_redirects=redirects)

def logout(client):
    return client.get(url_for('authbp.logout'), follow_redirects=False)

@pytest.mark.parametrize('auth_resp, user_data, next_url', [
    (None, [], 'authorize-info'),
    (benwa_resp(), [], '/authorize/signup'),
    (benwa_resp(), [test_user()], 'gallery')
])
def test_authorize_callback(client, mocker, auth_resp, user_data, next_url):
    users_uri = User().api_endpoint
    user = UserSchema(many=True).dump(user_data).data

    mocker.patch('benwaonline.auth.views.verify_token', return_value=auth_payload())
    mocker.patch('benwaonline.auth.views.handle_authorize_response', return_value=auth_resp)

    with requests_mock.Mocker() as mock:
        mock.get(users_uri, json=user)
        response = authenticate(client, mocker)

    assert response.status_code == 302
    assert next_url in response.headers['location']

def test_handle_authorize_response(client, mocker):
    mock_auth_response(mocker, None)
    assert handle_authorize_response() == None

def test_logout(client):
    response = logout(client)
    assert response.status_code == 302

# def test_get(client):
#     with client.session_transaction() as sess:
#         sess['access_token'] = 'access token'

#     response = client.get(url_for('authbp.signup'), follow_redirects=False)
#     assert response.status_code == 200
#     assert 'signup' in request.path

def users_dump():
    return UserSchema(many=True).dump([test_user()]).data

def empty_results():
    return {'data':[]}

@pytest.mark.parametrize('user_exists, authenticated', [
    (users_dump(), False),
    (empty_results(), True)
])
def test_signup_new_user(client, mocker, user_exists, authenticated):
    user = User(**test_user()).dump()
    mocker.patch('benwaonline.auth.views.verify_token', return_value=auth_payload())
    with requests_mock.Mocker() as mock:
        mock.get('/api/users', json=user_exists)
        mock.post('/api/users', json=user, status_code=201)
        resp = signup(client, 'access token')

    assert resp.status_code == 302
    assert current_user.is_authenticated == authenticated
