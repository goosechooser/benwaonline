from requests.auth import AuthBase
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

# from benwaonline we use BENWA to make twitter authenticate the user
# twitter AUTHENTICATES the user (via the user-agent)
# if user grants access, twitter redirects back to the auth-service
#   take response from twitter and generate access token (scope based on whether they exist or not)
# client receives response, login/register as needed
# and asks for a token
# BENWA authenticates the client (using client_id and client_secret)
#   and validates the authorization code

benwa = oauth.register(
    'benwaonline',
    app_key='BENWAONLINE',
)

class TokenAuth(AuthBase):
    '''Attaches a JWT to the given Request object'''
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r
