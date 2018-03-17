import os

BASE = os.path.abspath(os.path.dirname(__file__))

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
    MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', '192.168.99.100')
    MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11211))

class DevConfig(Config):
    DEBUG = True
    FRONT_URL_BASE = 'http://127.0.0.1'
    FRONT_URL = '{}:{}'.format(FRONT_URL_BASE, os.getenv('FRONT_PORT', '5000'))
    CALLBACK_URL = FRONT_URL
    API_URL = 'http://127.0.0.1:5001'
    AUTH_URL = 'http://127.0.0.1:5002'
    JWKS_URL = AUTH_URL + '/.well-known/jwks.json'
    BENWAONLINE_CONSUMER_KEY = 'nice'
    BENWAONLINE_CONSUMER_SECRET = 'ok'

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    FRONT_URL_BASE = 'http://127.0.0.1'
    FRONT_URL = '{}:{}'.format(FRONT_URL_BASE, os.getenv('FRONT_PORT', '5000'))
    CALLBACK_URL = FRONT_URL
    API_URL = 'mock://mock'
    AUTH_URL = 'mock://mock/'
    JWKS_URL = AUTH_URL + '/.well-known/jwks.json'
    MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11212))

class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    FRONT_URL_BASE = os.getenv('FRONT_URL')
    FRONT_URL = '{}:{}'.format(FRONT_URL_BASE, os.getenv('FRONT_PORT'))
    CALLBACK_URL = FRONT_URL_BASE
    API_URL = '{}:{}'.format(os.getenv('API_URL'), os.getenv('API_PORT'))
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
