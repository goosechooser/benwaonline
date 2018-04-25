import sys
import os
import pytest

from benwaonline import create_app
from benwaonline.config import TestConfig
from benwaonline.cache import cache as _cache

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

@pytest.fixture(scope='session')
def app():
    app = create_app('test')
    app.config.update(TestConfig.__dict__)

    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def cache():
    yield _cache
    _cache.clear()