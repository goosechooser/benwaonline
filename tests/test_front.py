import pytest

from flask import url_for

def test_search(client):
    data = {'tags': [''], 'submit': True}
    response = client.post('/', data=data, follow_redirects=False)
    assert response.status_code == 302
    assert url_for('gallery.show_posts') in response.headers['Location']

    data = {'tags': ['oldbenwa'], 'submit': True}
    response = client.post('/', data=data, follow_redirects=False)
    assert response.status_code == 302
    assert 'oldbenwa' in response.headers['Location']
    assert 'benwa' in response.headers['Location']