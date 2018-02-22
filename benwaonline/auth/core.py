import os
import requests
from flask import current_app
from jose import jwt, exceptions

from benwaonline.cache import cache
from benwaonline.config import app_config
from benwaonline.exceptions import BenwaOnlineAuthError

cfg = app_config[os.getenv('FLASK_CONFIG')]
ALGORITHMS = ['RS256']

def verify_token(token, jwks, audience=cfg.API_AUDIENCE, issuer=cfg.ISSUER):
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=audience,
                issuer=issuer
            )
        except jwt.ExpiredSignatureError as err:
            msg = 'Token provided by {} has expired'.format(
                unverified_header.get('sub', 'sub not found'))
            current_app.logger.info(msg)
            raise err
        except jwt.JWTClaimsError as err:
            raise BenwaOnlineAuthError(
                detail='{0}'.format(err),
                title='invalid claim',
                status=401
            )
        except exceptions.JWTError as err:
            raise BenwaOnlineAuthError(
                detail='{0}'.format(err),
                title='invalid signature',
                status=401
            )
        except Exception as err:
            raise BenwaOnlineAuthError(
                title='invalid header',
                detail='unable to parse authentication token'
            )
        return payload

    raise BenwaOnlineAuthError(
        title='invalid header', detail='unable to parse authentication token')


def get_jwks():
    rv = cache.get('jwks')
    if rv is None:
        try:
            current_app.logger.debug('JWKS not cached')
            jwksurl = requests.get(cfg.JWKS_URL, timeout=5)
        except requests.exceptions.Timeout:
            raise
        rv = jwksurl.json()
        cache.set('jwks', rv, expire=5*60)
    return rv


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
