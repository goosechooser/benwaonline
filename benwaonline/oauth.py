import os
from config import app_config
from requests.auth import AuthBase
from flask_login import UserMixin
from flask_oauthlib.client import OAuth

cfg = app_config[os.getenv('FLASK_CONFIG')]

oauth = OAuth()

auth0 = oauth.remote_app(
    'auth0',
    app_key='AUTH0',
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

class User(UserMixin):
    def __init__(self, id=None, username=None, created_on=None, user_id=None, active=None, comments=[], posts=[]):
        super().__init__()
        self.id = id
        self.username = username
        self.created_on = created_on
        self.user_id = user_id
        self.active = active
        self.comments = comments
        self.posts = posts