from datetime import datetime
import pytest
from benwaonline import benwaonline

# @pytest.fixture()
# def app(request, tmpdir_factory):
#     config = {
#         'DATABASE': str(fn),
#         'TESTING': True,
#     }

#     app = benwaonline(config=config)

#     with app.app_context():
#         init_db()
#         yield app

@pytest.fixture
def client(tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('temp')

    benwaonline.app.config['DATABASE'] = str(fn)
    benwaonline.app.config['TESTING'] = True

    client = benwaonline.app.test_client()
    with benwaonline.app.app_context():
        benwaonline.init_db()
        yield client

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

def test_login_logout(client):
    rv = login(client, benwaonline.app.config['USERNAME'],
                benwaonline.app.config['PASSWORD'])
    assert b'You logged in' in rv.data

    rv = logout(client)
    assert b'You logged out' in rv.data

    rv = login(client, benwaonline.app.config['USERNAME'] + 'x',
               benwaonline.app.config['PASSWORD'])
    assert b'Invalid username' in rv.data

    rv = login(client, benwaonline.app.config['USERNAME'],
               benwaonline.app.config['PASSWORD'] + 'x')
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
