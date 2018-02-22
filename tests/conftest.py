import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

import pytest

from benwaonline import create_app

@pytest.fixture(scope='session')
def app():
    test_app = create_app('test')

    with test_app.app_context():
        yield test_app
