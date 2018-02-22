import pytest

from benwaonline import create_app

@pytest.fixture(scope='session')
def app():
    test_app = create_app('test')

    with test_app.app_context():
        yield test_app
