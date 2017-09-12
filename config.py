import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'benwaonline.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'default'