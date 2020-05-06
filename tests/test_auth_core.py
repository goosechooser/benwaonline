from datetime import datetime, timedelta
import json
import pytest
from jose import jwt, exceptions
from benwaonline.exceptions import BenwaOnlineError
from benwaonline.auth import core

post_headers = {'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'}

def get_pem(fname):
    with open(fname, 'r') as f:
        return f.read()

with open('tests/data/test_jwks.json', 'r') as f:
        JWKS = json.load(f)

PRIV_KEY = get_pem('tests/data/benwaonline_test_priv.pem')
PUB_KEY = get_pem('tests/data/benwaonline_test_pub.pem')
ISSUER = 'issuer'
API_AUDIENCE = 'audience'

@pytest.fixture(scope='function')
def jwks(mocker):
    mocker.patch('benwaonline.auth.core.get_jwks', return_value=JWKS)

def jwt_headers():
    return {
        'typ': 'JWT',
        'alg': 'RS256',
        'kid': 'benwaonline_test'
    }

def jwt_claims():
    now = datetime.utcnow() - datetime(1970, 1, 1)
    exp_at = now + timedelta(seconds=300)

    return {
        'iss': ISSUER,
        'aud': API_AUDIENCE,
        'sub': '6969',
        'iat': now.total_seconds(),
        'exp': exp_at.total_seconds()
    }

def generate_jwt(claims, headers):
    ''' Generates a JWT'''
    return jwt.encode(claims, PRIV_KEY, algorithm='RS256', headers=headers)

@pytest.mark.parametrize('key, value', [
    ('aud', 'invalid'),
    ('iss', 'invalid')
])
def test_verify_token_invalid_claims(jwks, key, value):
    claims = jwt_claims()
    claims[key] = value

    token = generate_jwt(claims, jwt_headers())

    with pytest.raises(BenwaOnlineError):
        core.verify_token(token)

def test_verify_token_invalid_header_kid(jwks):
    headers = jwt_headers()
    headers['kid'] = 'invalid'

    token = generate_jwt(jwt_claims(), headers)

    with pytest.raises(BenwaOnlineError):
        core.verify_token(token)

def test_verify_token_expired(jwks, mocker):
    now = (datetime(1971, 1, 1) - datetime(1970, 1, 1))
    exp_at = now + timedelta(seconds=300)

    claims = jwt_claims()
    claims['iat'] = now.total_seconds()
    claims['exp'] = exp_at.total_seconds()

    token = generate_jwt(claims, jwt_headers())

    with pytest.raises(jwt.ExpiredSignatureError):
        core.verify_token(token)
