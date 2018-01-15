import os

BASE = os.path.abspath(os.path.dirname(__file__))

def get_secret(secret_name):
    '''Returns value provided by a docker secret, otherwise returns env'''
    try:
        with open('/run/secrets/' + secret_name, 'r') as f:
            data = f.read()
            return data.strip()
    except OSError:
        return os.getenv(secret_name)

class Config(object):
    BASE_DIR = BASE
    UPLOADED_IMAGES_DEST = '/static/'
    UPLOADED_BENWA_DIR = os.path.join(BASE, 'static', 'imgs')
    THUMBS_DIR = os.path.join(BASE, 'static', 'thumbs')
    REDIRECT_BACK_DEFAULT = 'gallery.show_posts'
    SECRET_KEY = 'not-so-secret'
    SECURITY_PASSWORD_SALT = 'super-secret'
    API_AUDIENCE = 'api audience'
    ISSUER = 'issuer'

class DevConfig(Config):
    DEBUG = True
    API_URL = 'http://127.0.0.1:5001/api'
    AUTH_URL = 'http://127.0.0.1:5002'
    JWKS_URL = AUTH_URL + '/.well-known/jwks.json'
    BENWAONLINE_CONSUMER_KEY = 'nice'
    BENWAONLINE_CONSUMER_SECRET = 'ok'

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    API_URL = 'mock://mock/api'
    AUTH_URL = 'mock://mock/'
    JWKS_URL = AUTH_URL + '/.well-known/jwks.json'

class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = get_secret('SECRET_KEY')
    SECURITY_PASSWORD_SALT = get_secret('SECURITY_PASSWORD_SALT')
    FRONT_URL_BASE = os.getenv('FRONT_URL')
    FRONT_URL = '{}:{}'.format(FRONT_URL_BASE, os.getenv('FRONT_PORT'))
    API_URL = '{}:{}/api'.format(os.getenv('API_URL'), os.getenv('API_PORT'))
    AUTH_URL = '{}:{}'.format(os.getenv('AUTH_URL'), os.getenv('AUTH_PORT'))
    JWKS_URL = AUTH_URL + '/.well-known/jwks.json'
    ISSUER = 'https://benwa.online'
    API_AUDIENCE = 'https://benwa.online/api'
    BENWAONLINE_CONSUMER_KEY = os.getenv('BENWA_CONSUMER_KEY')
    BENWAONLINE_CONSUMER_SECRET = os.getenv('BENWA_CONSUMER_SECRET')

app_config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}
