import os
from requests.auth import AuthBase

from flask_oauthlib.client import OAuth
from config import app_config

cfg = app_config[os.getenv('FLASK_CONFIG')]

oauth = OAuth()

auth0 = oauth.remote_app(
    'auth0',
    app_key='AUTH0',
    # consumer_key = cfg.AUTH0_CONSUMER_KEY,
    # consumer_secret = cfg.AUTH0_CONSUMER_SECRET,
    request_token_params={
        'scope': 'openid profile delete:other-comments',
        'audience': cfg.API_AUDIENCE,
        'connection': 'twitter'
    },
    base_url='https://' + cfg.AUTH0_DOMAIN + '/',
    access_token_method='POST',
    access_token_url='/oauth/token',
    authorize_url='/authorize',
)

class TokenAuth(AuthBase):
    '''Attaches a JWT to the given Request object'''
    def __init__(self, token, token_type):
        self.token = token
        self.token_type = token_type

    def __call__(self, r):
        r.headers['Authorization'] = self.token_type + ' ' + self.token
        return r
