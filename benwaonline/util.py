"""
Contains any utility functions used by processors or the benwaonline frontend.
"""
import os
import requests
from jose import jwt, exceptions
from flask import session
from flask_restless import ProcessingException
from flask_restless.views.base import catch_processing_exceptions
from werkzeug.contrib.cache import SimpleCache

from config import app_config

cfg = app_config[os.getenv('FLASK_CONFIG')]

cache = SimpleCache()
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
            raise
        except jwt.JWTClaimsError as err:
            raise
        except exceptions.JWTError as err:
            raise
        except Exception as err:
            raise
        return payload

    raise Exception

def get_jwks():
    rv = cache.get('jwks')
    if rv is None:
        try:
            jwksurl = requests.get(cfg.JWKS_URL, timeout=5)
        except requests.exceptions.Timeout:
            raise
        rv = jwksurl.json()
        cache.set('jwks', rv, timeout=48 * 3600)
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
