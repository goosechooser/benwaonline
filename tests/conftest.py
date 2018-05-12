import sys
import os
import pytest

from flask.cli import load_dotenv
load_dotenv()

from benwaonline import create_app
from benwaonline.cache import cache as _cache

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')

    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def cache():
    yield _cache
    _cache.clear()