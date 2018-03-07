from datetime import datetime, timedelta
import json
import pytest
import requests_mock
from flask import url_for, current_app
from jose import jwt, exceptions
from benwaonline.exceptions import BenwaOnlineError
from benwaonline.oauth import benwa
from benwaonline.auth import core

post_headers = {'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'}

def get_pem(fname):
    with open(fname, 'r') as f:
        return f.read()

PRIV_KEY = get_pem('tests/data/benwaonline_test_priv.pem')
PUB_KEY = get_pem('tests/data/benwaonline_test_pub.pem')
ISSUER = 'issuer'
API_AUDIENCE = 'audience'

@pytest.fixture(scope='function')
def jwks():
    with open('tests/data/test_jwks.json', 'r') as f:
        JWKS = json.load(f)

    with requests_mock.Mocker() as mock:
        mock.get(current_app.config['JWKS_URL'], json=JWKS)
        yield

def generate_jwt(claims, headers=None):
    ''' Generates a JWT'''
    if not headers:
        headers = {
            'typ': 'JWT',
            'alg': 'RS256',
            'kid': 'benwaonline_test'
        }
    return jwt.encode(claims, PRIV_KEY, algorithm='RS256', headers=headers)

@pytest.mark.usefixtures('cache')
class TestVerifyToken(object):
    def test_invalid_header_kid(self, jwks):
        now = (datetime.utcnow() - datetime(1970, 1, 1))
        exp_at = now + timedelta(seconds=300)

        headers = {
                'typ': 'JWT',
                'alg': 'RS256',
                'kid': 'invalid'
        }

        claims = {
            'iss': ISSUER,
            'aud': API_AUDIENCE,
            'sub': '6969',
            'iat': now.total_seconds(),
            'exp': exp_at.total_seconds()
        }

        token = generate_jwt(claims, headers=headers)

        with pytest.raises(BenwaOnlineError):
            core.verify_token(token)


    def test_invalid_audience(self, jwks):
        claims = {
            'iss': ISSUER,
            'aud': 'invalid'
        }
        token = generate_jwt(claims)

        with pytest.raises(BenwaOnlineError):
            core.verify_token(token)

    def test_invalid_issuer(self, jwks):
        claims = {
            'iss': 'invalid',
            'aud': API_AUDIENCE
        }
        token = generate_jwt(claims)
        with pytest.raises(BenwaOnlineError):
            core.verify_token(token)

    def test_expired(self, jwks):
        now = (datetime(1971, 1, 1) - datetime(1970, 1, 1))
        exp_at = now + timedelta(seconds=300)

        claims = {
            'iss': ISSUER,
            'aud': API_AUDIENCE,
            'sub': '6969',
            'iat': now.total_seconds(),
            'exp': exp_at.total_seconds()
        }

        token = generate_jwt(claims)
        with pytest.raises(jwt.ExpiredSignatureError):
            core.verify_token(token)
