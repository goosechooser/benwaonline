import pytest
import requests_mock
from flask import url_for
import utils

def tags_data():
    return utils.load_test_data('show_tags.json')

def test_show_tags(client):
    with requests_mock.Mocker() as mock:
        mock.get('/api/tags', json=tags_data())
        resp = client.get(url_for('tags.show_tags'))

    assert resp.status_code == 200