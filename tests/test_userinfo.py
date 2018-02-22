import pytest
import requests_mock
from flask import url_for, render_template, current_app, json
from benwaonline.entities import User, Post, Like, Comment
from benwaonline.userinfo.views import show_user, show_comments
from benwaonline.exceptions import BenwaOnlineException
from tests.helpers.utils import error_response, load_test_data

class TestShowUsers(object):
    users_uri = User().api_endpoint
    test_data = load_test_data('show_users.json')

    def test_no_users(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.users_uri, json={'data': []})
            response = client.get(url_for('userinfo.show_users'))
            assert response.status_code == 200

class TestShowUser(object):
    user_uri = User(id=1).instance_uri
    posts_uri = User(id=1).resource_uri(Post())
    likes_uri = User(id=1).resource_uri(Like())

    test_data = load_test_data('show_user.json')

    def test_no_posts(self, client):
        user = User(id=1)
        result = render_template('user.html', user=user)
        assert 0 == result.count('gallery/show/')

    def test_no_user(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.user_uri, status_code=404, json=error_response('User', 1))
            response = client.get(url_for('userinfo.show_user', user_id=1))
            assert response.status_code == 200

    def test_no_user_raises_exception(self):
        with requests_mock.Mocker() as mock:
            mock.get(self.user_uri, status_code=404, json=error_response('User', 1))
            with pytest.raises(BenwaOnlineException):
                show_user(user_id=1)

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
    comments_uri = User(id=1).resource_uri(Comment())
    comments = load_test_data('userinfo_show_comments.json')

    def test_no_user(self, client):
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, status_code=404, json=error_response('User', 1))

            response = client.get(url_for('userinfo.show_comments', user_id=1))
            assert response.status_code == 200

    def test_no_user_raises_exception(self):
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, status_code=404, json=error_response('User', 1))
            with pytest.raises(BenwaOnlineException):
                show_comments(1)

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
