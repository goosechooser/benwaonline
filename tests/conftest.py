import os
import pytest

from benwaonline import create_app
from benwaonline.database import db as _db

# TESTDB = 'test_project.db'
# TESTDB_PATH = "/tests/{}".format(TESTDB)
TEST_DATABASE_URI = 'sqlite://' #+ TESTDB_PATH

@pytest.fixture(scope='session')
def app():
    config = {
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'TESTING': True,
    }

    app = create_app(config=config)

    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    # if os.path.exists(TESTDB_PATH):
    #     os.unlink(TESTDB_PATH)

    _db.app = app
    _db.create_all()

    yield _db

    _db.drop_all()
    # os.unlink(TESTDB_PATH)

@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()
