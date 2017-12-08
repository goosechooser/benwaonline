import os

BASE = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    BASE_DIR = BASE
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_IMAGES_DEST = '/static/'
    UPLOADED_BENWA_DIR = os.path.join(BASE, 'benwaonline', 'static', 'imgs')
    THUMBS_DIR = os.path.join(BASE, 'benwaonline', 'static', 'thumbs')
    REDIRECT_BACK_DEFAULT = 'gallery.show_posts'
    SECRET_KEY = 'not-so-secret'
    SECURITY_PASSWORD_SALT = 'super-secret'
    API_AUDIENCE = 'https://api.benwa.online'
    AUTH0_DOMAIN = 'choosegoose.auth0.com'
    AUTH0_CONSUMER_KEY = ''
    AUTH0_CONSUMER_SECRET = ''
    JWKS_URL = 'https://' + AUTH0_DOMAIN + '/.well-known/jwks.json'

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/benwaonline'
    DEBUG = True
    SECRET_KEY = 'not-so-secret'
    API_URL = "http://127.0.0.1:5001/api"

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    API_URL = 'mock://mock/api'

class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = ''
    SECURITY_PASSWORD_SALT = ''
    API_URL = 'https://benwa.online/api'

app_config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}
