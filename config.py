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
    UPLOADED_BENWA_DIR = os.path.join(BASE, 'benwaonline', 'static', 'imgs')
    THUMBS_DIR = os.path.join(BASE, 'benwaonline', 'static', 'thumbs')
    REDIRECT_BACK_DEFAULT = 'gallery.show_posts'
    SECRET_KEY = 'not-so-secret'
    SECURITY_PASSWORD_SALT = 'super-secret'
    API_AUDIENCE = get_secret('API_AUDIENCE')
    AUTH0_DOMAIN = get_secret('AUTH0_DOMAIN')
    AUTH0_CONSUMER_KEY = ''
    AUTH0_CONSUMER_SECRET = ''
    JWKS_URL = 'https://' + AUTH0_DOMAIN + '/.well-known/jwks.json'

class DevConfig(Config):
    DEBUG = True
    API_URL = 'http://127.0.0.1:5001/api'

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    API_URL = 'mock://mock/api'

class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = get_secret('SECRET_KEY')
    SECURITY_PASSWORD_SALT = get_secret('SECURITY_PASSWORD_SALT')
    API_URL = '{}:{}/api'.format(os.getenv('API_URL'), os.getenv('API_PORT'))

app_config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}
