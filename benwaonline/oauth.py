import os
from config import app_config
from requests.auth import AuthBase
from flask_oauthlib.client import OAuth

cfg = app_config[os.getenv('FLASK_CONFIG')]

oauth = OAuth()

# Realized machine-to-machine authentication aint free with Auth0
# Gotta write me own oauth2 server RIP
# auth0 = oauth.remote_app(
#     'auth0',
#     app_key='AUTH0',
#     request_token_params={
#         'scope': 'openid profile delete:other-comments',
#         'audience': cfg.API_AUDIENCE,
#         'connection': 'twitter'
#     },
#     base_url='https://' + cfg.AUTH0_DOMAIN + '/',
#     access_token_method='POST',
#     access_token_url='/oauth/token',
#     authorize_url='/authorize',
# )

class TokenAuth(AuthBase):
    '''Attaches a JWT to the given Request object'''
    def __init__(self, token, token_type):
        self.token = token
        self.token_type = token_type

    def __call__(self, r):
        r.headers['Authorization'] = self.token_type + ' ' + self.token
        return r
