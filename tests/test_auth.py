from datetime import datetime
import pytest
import jose
import requests_mock

from flask import url_for, request, current_app
from flask_login import current_user
from benwaonline.schemas import UserSchema
from benwaonline.entities import User
from benwaonline.auth.views import check_username
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

JWKS = {'yea': 'im a jwks'}

def authenticate(client, mocker, resp, jwks):
    mocker.patch('benwaonline.auth.views.benwa.authorized_response', return_value=resp)
    mocker.patch('benwaonline.auth.views.get_jwks', return_value=jwks)
    return client.get(url_for('authbp.authorize_callback'), follow_redirects=False)

def signup(client, redirects=False):
    form = {'adjective': 'Beautiful', 'benwa': 'Benwa', 'noun': 'Aficionado', 'submit': True}
    return client.post(url_for('authbp.signup'), data=form, follow_redirects=redirects)

def logout(client):
    return client.get(url_for('authbp.logout'), follow_redirects=False)

class TestAuthorizeCallback(object):
    users_uri = User().api_endpoint

    def test_valid_auth_new_user(self, client, mocker):
        payload['sub'] = '59866969'
        mocker.patch('benwaonline.auth.views.verify_token', return_value=payload)

        with requests_mock.Mocker() as mock:
            mock.get(self.users_uri, json={'data': []}, status_code=404)
            response = authenticate(client, mocker, benwa_resp, JWKS)

        assert response.status_code == 302
        assert url_for('authbp.signup') in response.headers['location']

    def test_valid_auth_old_user(self, client, mocker):
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
            mock.get(self.users_uri, json=user)
            response = authenticate(client, mocker, benwa_resp, JWKS)

        assert response.status_code == 302
        assert current_user.is_authenticated
        assert 'gallery' in response.headers['location']

    def test_no_authorized_response(self, client, mocker):
        response = authenticate(client, mocker, None, JWKS)
        assert response.status_code == 400

def test_logout(client):
    response = logout(client)
    assert response.status_code == 302

class TestCheckUsername(object):
    users_uri = User().api_endpoint
    username = 'Benwa Benwa Benwa'

    @pytest.fixture
    def mock(self):
        with requests_mock.Mocker() as mock:
            yield mock

    def test_username_found(self, client, mock):
        mock.get(self.users_uri, status_code=200)
        resp = check_username(self.username)
        assert 'Username [Benwa Benwa Benwa] already in use, please select another' in resp

    def test_username_not_found(self, client, mock):
        mock.get(self.users_uri, status_code=404)
        resp = check_username(self.username)
        assert not resp

class TestSignup(object):
    users_uri = User().api_endpoint
    user_uri = User(id=1).instance_uri

    user = UserSchema().dump({
        'id': '1',
        "active": True,
        "created_on": datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Fan"
    }).data

    def test_get(self, client, mocker):
        response = client.get(url_for('authbp.signup'), follow_redirects=False)
        assert response.status_code == 200
        assert 'signup' in request.path

    def test_post(self, client, mocker):
        with client.session_transaction() as sess:
            sess['access_token'] = 'Bearer ' + 'access token'

        with requests_mock.Mocker() as mock:
            mock.get(self.users_uri, json=error_response('User', 1), status_code=404)
            mock.post(self.users_uri, json=self.user, status_code=201)
            resp = signup(client)

            assert resp.status_code == 302
            assert current_user.is_authenticated

            mock.get(self.user_uri, json=self.user)
            response = logout(client)
            assert response.status_code == 302
            assert not current_user.is_authenticated

    def test_username_exists(self, client, mocker):
        with requests_mock.Mocker() as mock:
            mock.get(self.users_uri, json=self.user, status_code=200)
            mock.get(self.user_uri, status_code=200)
            resp = signup(client)

        assert 'signup' in request.path
