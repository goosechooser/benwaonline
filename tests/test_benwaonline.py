import os
from datetime import datetime
import pytest

from benwaonline import add_benwas
from benwaonline import models

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

def test_add_benwas():
    entries = models.BenwaPicture.query.all()
    assert not entries

    add_benwas()
    entries = models.BenwaPicture.query.all()
    assert len(entries) == 2

# Making sure links go to the correct place is ?
def test_rotating(client):
    rv = client.get('/rotating', follow_redirects=True)
    print(rv.data)
    assert b'rotating/2'

def test_benwa_schema(session):
    test_benwa = models.Benwa(name='test_benwa')
    session.add(test_benwa)

    assert models.Benwa.query.filter_by(name='test_benwa').one()

    pic = models.BenwaPicture(filename='help.jpg', date_posted=datetime.utcnow(),\
                             views=0, owner=test_benwa)
    session.add(pic)

    gb = models.GuestbookEntry(owner=test_benwa)
    session.add(gb)

    session.commit()
