import sys
import os
import pytest

from benwaonline import create_app
from benwaonline.cache import cache as _cache

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

@pytest.fixture(scope='session')
def app():
    test_app = create_app('test')

    with test_app.app_context():
        yield test_app

@pytest.fixture(scope='session')
def cache():
    yield _cache
    _cache.flush_all()