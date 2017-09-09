import os
import pytest

from benwaonline import add_benwas
from benwaonline.models import BenwaPicture

@pytest.fixture
def client(app, db):
    app.db = db

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

# def test_login_logout(client, app):
#     rv = login(client, app.config['USERNAME'],
#                 app.config['PASSWORD'])
#     assert b'You logged in' in rv.data

#     rv = logout(client)
#     assert b'You logged out' in rv.data

#     rv = login(client, app.config['USERNAME'] + 'x',
#                app.config['PASSWORD'])
#     assert b'Invalid username' in rv.data

#     rv = login(client, app.config['USERNAME'],
#                app.config['PASSWORD'] + 'x')
#     assert b'Invalid password' in rv.data

def test_guestbook(client):
    rv = client.get('/guestbook')
    assert b'plse leave commen,' in rv.data

    rv = client.post('/guestbook/add', data=dict(
        name='benwa NAME',
        content='benwa CONTENT'
    ), follow_redirects=True)

    print(rv.data)
    assert b'benwa NAME' in rv.data
    assert b'benwa CONTENT' in rv.data

def test_rotating(client):
    entries = BenwaPicture.query.all()
    assert not entries

    add_benwas()
    entries = BenwaPicture.query.all()
    assert len(entries) == 2
