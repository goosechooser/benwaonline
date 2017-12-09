import pytest

from benwaonline import create_app

@pytest.fixture(scope='session')
def testdir(tmpdir_factory):
    fn = tmpdir_factory.mktemp('test')
    yield fn

@pytest.fixture(scope='session')
def app(testdir):
    app = create_app('test')

    with app.app_context():
        yield app
