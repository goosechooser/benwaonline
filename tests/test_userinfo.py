import pytest
import requests_mock
from marshmallow import pprint
from flask import url_for, render_template, current_app, json
from benwaonline import mappers
from benwaonline.entities import User, Post, Comment, Tag
from benwaonline.userinfo.views import show_user, show_comments, combine_tags
from benwaonline.exceptions import BenwaOnlineError, BenwaOnlineRequestError
import utils

class TestShowUsers(object):
    users_uri = mappers.collection_uri(User())
    test_data = utils.load_test_data('show_users.json')

    def test_no_users(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.users_uri, json={'data': []})
            response = client.get(url_for('userinfo.show_users'))
            assert response.status_code == 200

class TestShowUser(object):
    user_uri = mappers.instance_uri(User(id=1))
    posts_uri = mappers.resource_uri(User(id=1), 'posts')
    likes_uri = mappers.resource_uri(User(id=1), 'likes')
    test_data = utils.load_test_data('show_user.json')

    def test_no_posts(self, client):
        user = User(id=1)
        result = render_template('user.html', user=user)
        assert 0 == result.count('gallery/show/')

    @pytest.mark.usefixtures('cache')
    def test_no_user(self, client):
        with requests_mock.Mocker() as mock:
            mock.get('/api/users/1', status_code=404, json=utils.error_response('User', 1))
            response = client.get(url_for('userinfo.show_user', user_id=1))
            assert response.status_code == 200

    @pytest.mark.usefixtures('cache')
    def test_no_user_raises_exception(self):
        with requests_mock.Mocker() as mock:
            mock.get('/api/users/1', status_code=404, json=utils.error_response('User', 1))
            with pytest.raises(BenwaOnlineError):
                show_user(user_id=1)

    @pytest.mark.usefixtures('cache')
    def test_show_user(self, client):
        user = self.test_data['user']
        posts = self.test_data['user_posts']

        with requests_mock.Mocker() as mock:
            mock.get(self.user_uri, json=user)
            mock.get(self.posts_uri, json=posts)
            mock.get(self.likes_uri, json=posts)
            response = client.get(url_for('userinfo.show_user', user_id=1))
            assert response.status_code == 200

class TestShowComments(object):
    comments_uri = mappers.resource_uri(User(id=1), 'comments')
    comments = utils.load_test_data('show_comments.json')['comments_with_previews']

    def test_no_user(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, status_code=404, json=utils.error_response('User', 1))

            response = client.get(url_for('userinfo.show_comments', user_id=1))
            assert response.status_code == 200

    def test_user_no_comments(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, json={'data':[]})
            response = client.get(url_for('userinfo.show_comments', user_id=1))
            assert response.status_code == 200

    def test_user_with_comments(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, json=self.comments)
            response = client.get(url_for('userinfo.show_comments', user_id=1))
            assert response.status_code == 200

def test_show_likes_no_user(client):
    # test no tags?
    with requests_mock.Mocker() as mock:
        mock.get('/api/users/1/likes', status_code=404, json=utils.error_response('User', 1))
        response = client.get(url_for('userinfo.show_likes', user_id=1))
        assert response.status_code == 200