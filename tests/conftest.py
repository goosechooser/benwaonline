import os
import pytest

from benwaonline import create_app
from benwaonline.database import db as _db
from scripts.setup_db import init_roles, init_tags

@pytest.fixture(scope='session')
def testdir(tmpdir_factory):
    fn = tmpdir_factory.mktemp('test')
    yield fn

@pytest.fixture(scope='session')
def app(testdir):
    app = create_app('test')
    app.config['UPLOADED_IMAGES_DEST'] = testdir
    app.config['UPLOADED_BENWA_DIR'] = str(testdir)

    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    _db.app = app
    _db.create_all()

    init_roles(_db.session)
    init_tags(_db.session)

    yield _db

    _db.drop_all()

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
