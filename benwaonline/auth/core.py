import os
import requests
from flask import current_app
from jose import jwt, exceptions

from benwaonline.cache import cache
from benwaonline.config import app_config
from benwaonline.exceptions import BenwaOnlineAuthError

cfg = app_config[os.getenv('FLASK_CONFIG')]
ALGORITHMS = ['RS256']

def verify_token(token):
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = match_key_id(unverified_header)

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=cfg.API_AUDIENCE,
            issuer=cfg.ISSUER
        )
    except jwt.ExpiredSignatureError as err:
        handle_expired_signature(err)
    except jwt.JWTClaimsError as err:
        handle_claims(err)
    except exceptions.JWTError as err:
        handle_jwt(err)
    except Exception as err:
        handle_non_jwt()
    return payload


def match_key_id(unverified_header):
    """Checks if the RSA key id given in the header exists in the JWKS."""
    jwks = get_jwks()
    rsa_keys = [
        rsa_from_jwks(key)
        for key in jwks["keys"]
        if key["kid"] == unverified_header["kid"]
    ]
    try:
        return rsa_keys[0]
    except IndexError:
        return None

def rsa_from_jwks(key):
    return {
        "kty": key["kty"],
        "kid": key["kid"],
        "use": key["use"],
        "n": key["n"],
        "e": key["e"]
    }


def handle_claims(err):
    """Handles tokens with invalid claims"""
    raise BenwaOnlineAuthError(
        detail='{0}'.format(err),
        title='invalid claim',
        status=401
    )

def handle_expired_signature(err):
    """Handles tokens with expired signatures."""
    raise err

def handle_jwt(err):
    """Handles tokens with other jwt-related issues."""
    raise BenwaOnlineAuthError(
        detail='{0}'.format(err),
        title='invalid signature',
        status=401
    )

def handle_non_jwt():
    """Handles everything else."""
    raise BenwaOnlineAuthError(
        title='invalid header',
        detail='unable to parse authentication token'
    )

@cache.cached(timeout=48 * 3600, key_prefix='jwks')
def get_jwks():
    try:
        msg = 'JWKS not cached - requesting from {}'.format(current_app.config['JWKS_URL'])
        current_app.logger.debug(msg)

        jwksurl = requests.get(current_app.config['JWKS_URL'], timeout=5)
        jwks = jwksurl.json()
    except requests.exceptions.Timeout:
        raise BenwaOnlineAuthError(
            title='JWKS Request Timed Out',
            detail='the authentication server is unavailable, or another issue has occured',
            status=500
        )

    return jwks

def has_scope(scope, token):
    unverified_claims = jwt.get_unverified_claims(token)
    token_scopes = unverified_claims['scope'].split()
    return True if scope in token_scopes else False


def refresh_token_request(client, refresh_token):
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client.consumer_key,
        'client_secret': client.consumer_secret
    }

    resp = requests.post(client.base_url + client.access_token_url, data=data)
    return resp.json()
