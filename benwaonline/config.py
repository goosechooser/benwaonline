import os

BASE = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Need to re-examine this later, maby
    BASE_DIR = BASE
    UPLOADED_IMAGES_DEST = '/static/'
    UPLOADED_BENWA_DIR = os.path.join(BASE, 'static', 'imgs')
    THUMBS_DIR = os.path.join(BASE, 'static', 'thumbs')

    API_AUDIENCE = 'api audience'
    ISSUER = 'issuer'
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    API_URL = '{}:{}'.format(os.getenv('API_HOST'), os.getenv('API_PORT', ''))
    AUTH_URL = '{}:{}'.format(os.getenv('AUTH_HOST'), os.getenv('AUTH_PORT', ''))
    JWKS_URL = AUTH_URL + '/.well-known/jwks.json'
    CALLBACK_URL = '{}'.format(os.getenv('FRONT_HOST'))

    BENWAONLINE = {
        'consumer_key': os.getenv('BENWAONLINE_CONSUMER_KEY'),
        'consumer_secret': os.getenv('BENWAONLINE_CONSUMER_SECRET'),
        'request_token_params': {
            'scopes': '',
            'audience': API_URL
        },
        'base_url': AUTH_URL,
        'access_token_method': 'POST',
        'access_token_url': '/oauth/token',
        'authorize_url': '/authorize'
    }

class DevConfig(Config):
    pass

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    API_URL = 'mock://mock'
    AUTH_URL = 'mock://mock/'
    JWKS_URL = AUTH_URL + '/.well-known/jwks.json'

class ProdConfig(Config):
    ISSUER = 'https://benwa.online'
    API_AUDIENCE = 'https://benwa.online/api'
    CALLBACK_URL = os.getenv('FRONT_HOST')

app_config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig
}
