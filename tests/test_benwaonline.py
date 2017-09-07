from datetime import datetime
import pytest
from benwaonline import create_app
from benwaonline.blueprints.benwaonline import init_db

@pytest.fixture()
def app(request, tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('temp')
    config = {
        'DATABASE': str(fn),
        'TESTING': True,
    }

    app = create_app(config=config)

    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app, tmpdir_factory):
    with app.test_client() as c:
        yield c

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_empty_db(client):
    rv = client.get('/guestbook')
    assert b'plse leave commen,' in rv.data

def test_login_logout(client, app):
    rv = login(client, app.config['USERNAME'],
                app.config['PASSWORD'])
    assert b'You logged in' in rv.data

    rv = logout(client)
    assert b'You logged out' in rv.data

    rv = login(client, app.config['USERNAME'] + 'x',
               app.config['PASSWORD'])
    assert b'Invalid username' in rv.data

    rv = login(client, app.config['USERNAME'],
               app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in rv.data

def test_guestbook(client):
    rv = client.get('/guestbook')
    assert b'plse leave commen,' in rv.data
    date = datetime.utcnow().strftime('%d/%m/%Y')

    rv = client.post('/guestbook/add', data=dict(
        name='benwa',
        comment='benwa text',
        date=date
    ), follow_redirects=True)

    assert b'benwa' in rv.data
    assert b'benwa text' in rv.data
    assert bytes(date, encoding='utf-8') in rv.data
