import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'benwaonline.db')
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'default'