import pytest
import requests_mock
from flask import url_for, json
from benwaonline.entities import Comment

class TestShowComments(object):
    comments_uri = Comment().api_endpoint

    with open('tests/data/show_comments.json') as f:
        test_data = json.load(f)

    def test_no_comments(self, client):
        comments = {'data': []}
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, json=comments)
            response = client.get(url_for('comments.show_comments'))
            assert response.status_code == 200

    @pytest.mark.skip
    def test_comments_no_previews(self, client):
        comments = self.test_data['comments_no_previews']
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, json=comments)
            response = client.get(url_for('comments.show_comments'))
            assert response.status_code == 200

    def test_comments_with_previews(self, client):
        comments = self.test_data['comments_with_previews']
        with requests_mock.Mocker() as mock:
            mock.get(self.comments_uri, json=comments)
            response = client.get(url_for('comments.show_comments'))
            assert response.status_code == 200
