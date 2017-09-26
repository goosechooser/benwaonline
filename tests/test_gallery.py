from datetime import datetime
import pytest
from flask import g, url_for
from benwaonline.models import Post, Tag, User

def test_show_posts(client, session):
    # tag_benwa = Tag(name='benwa')
    # tag_old_benwa = Tag(name='old_benwa')
    # session.add(tag_benwa)
    # session.add(tag_old_benwa)

    # post = Post(title='test', created=datetime.utcnow(), tags=[tag_benwa])
    # session.add(post)

    # post2 = Post(title='test', created=datetime.utcnow(), tags=[tag_old_benwa])
    # session.add(post2)

    response = client.get('/gallery')
    assert response.status_code == 301
    assert 'gallery' in response.headers['Location']

    response = client.get('/gallery/')
    assert response.status_code == 200

    response = client.get('/gallery/benwa')
    assert response.status_code == 301
    assert 'gallery/benwa' in response.headers['Location']

    response = client.get('/gallery/benwa oldbenwa', follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/gallery/benwa oldbenwa')
    assert response.status_code == 301
    assert 'gallery/benwa%20oldbenwa' in response.headers['Location']

def test_show_post_redirect(client, session):
    response = client.get('/gallery/show', follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/gallery/show', follow_redirects=False)
    assert response.status_code == 301
    assert 'gallery/' in response.headers['Location']

def test_show_post(client, session):
    response = client.get('/gallery/show/1', follow_redirects=False)
    assert response.status_code == 302
    assert 'gallery/' in response.headers['Location']

    post = Post(title='test', created=datetime.utcnow())
    session.add(post)

    response = client.get('/gallery/show/1')
    assert response.status_code == 200

# This may be too big for a unit test?
def test_add_comment(client, session, mocker):
    # Set up post
    post = Post(title='test', created=datetime.utcnow())
    session.add(post)

    # Set up a user
    resp = {'x_auth_expires': '0', 'oauth_token_secret': 'secret',
            'user_id': '420', 'oauth_token': '59866969-token', 'screen_name': 'tester'}

    mocker.patch('benwaonline.oauth.twitter.authorized_response', return_value=resp)
    response = client.get(url_for('benwaonline.oauthorize'), follow_redirects=False)

    form = {'adj': 'beautiful', 'benwa': 'benwa', 'pos': 'lover', 'submit': True}
    response = client.post('/signup', data=form, follow_redirects=True)

    comment = {'content': 'test comment'}
    response = client.post('/gallery/show/1/add', data=comment)

    user = User.query.first()
    user_comment = user.comments.one()
    assert user_comment.content == 'test comment'

    post_comment = post.comments.one()
    assert post_comment.content == 'test comment'

    assert user_comment == post_comment

# def test_show_post_previous_next(client, session):
#     post = Post(title='test', created=datetime.utcnow())
#     session.add(post)

#     post = Post(title='test2', created=datetime.utcnow())
#     session.add(post)

#     response = client.get('/gallery/show/1/next')
#     assert response.status_code == 302
#     assert 'gallery/show/2' in response.headers['Location']

#     response = client.get('/gallery/show/2/previous')
#     assert response.status_code == 302
#     assert 'gallery/show/1' in response.headers['Location']


# def test_add_post(client, session):
#     img_path = 'benwaonline/static/benwas/test.png'
#     preview_path = 'benwaonline/static/benwas/preview.png'
#     add_post(img_path, preview_path)

#     post = Post.query.first()

#     # Dog I hate paths
#     # assert post.image.filepath == os.path.relpath(img_path, 'benwaonline/static/')
#     # assert post.preview.filepath == preview_path
#     # Figure out better way to check if List of tags contains name of
#     assert post.tags[0].name == 'benwa'

# def test_add_posts(session):
#     img_path = 'benwaonline/static/benwas/imgs'
#     preview_path = 'benwaonline/static/benwas/thumbs'
#     add_posts(img_path, preview_path)

#     posts = Post.query.all()
#     for post in posts:
#         print(post.tags.count)
#         _, img_tail = os.path.split(post.image.filepath)
#         print(img_tail)
#         _, preview_tail = os.path.split(post.preview.filepath)
#         print(preview_tail)

#         assert img_tail == preview_tail
#         # assert post.preview.filepath == preview_path
#         assert post.tags[0].name == 'benwa'