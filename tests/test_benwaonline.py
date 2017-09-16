import os
from datetime import datetime
import pytest

from benwaonline import add_benwas
from benwaonline.models import *
from scripts.add_benwas import add_post

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

# def test_empty_db(client):
#     rv = client.get('/guestbook')
#     assert b'plse leave commen,' in rv.data

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

# def test_guestbook(client):
#     rv = client.get('/guestbook')
#     assert b'plse leave commen,' in rv.data

#     rv = client.post('/guestbook/add', data=dict(
#         name='benwa NAME',
#         content='benwa CONTENT'
#     ), follow_redirects=True)

#     print(rv.data)
#     assert b'benwa NAME' in rv.data
#     assert b'benwa CONTENT' in rv.data

def test_tag(session):
    created = datetime.utcnow()
    name = 'benwa'
    tag = Tag(name=name, created=created)
    session.add(tag)
    q = Tag.query.first()

    assert q
    assert q.id == 1
    assert q.name == name
    assert q.created == created

def test_post(session):
    tag_name = 'benwa'
    title = 'Benwas the best'
    created = datetime.utcnow()

    tag = Tag(name=tag_name, created=created)
    session.add(tag)

    post = Post(title=title, created=created)
    post.tags.append(tag)
    session.add(post)

    q = Post.query.first()

    assert q
    assert q.id == 1
    assert q.title == title
    assert q.created == created
    assert len(q.tags) == 1
    assert Post.query.filter(Post.tags.any(name=tag_name))

def test_add_post(session):
    img_path = 'test.png'
    preview_path = 'preview.png'
    add_post(img_path, preview_path)

    post = Post.query.first()

    assert post.image.filepath == img_path
    assert post.preview.filepath == preview_path
    assert 'benwa' == post.tags[0].name



# def test_post(session):
#     test_benwa = models.Benwa(name='test_benwa')
#     session.add(test_benwa)

#     assert models.Benwa.query.filter_by(name='test_benwa').one()

#     pic = models.BenwaPicture(filename='help.jpg', date_posted=datetime.utcnow(),\
#                              views=0, owner=test_benwa)
#     session.add(pic)

#     gb = models.GuestbookEntry(owner=test_benwa)
#     session.add(gb)

#     session.commit()

# def test_add_benwas():
#     entries = Post.query.all()
#     assert not entries

#     add_benwas()
#     entries Post.query.all()
#     assert entries

