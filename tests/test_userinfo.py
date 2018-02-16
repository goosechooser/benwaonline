import pytest
from flask import url_for, render_template
from benwaonline.entities import User

def test_show_user_no_posts(client):
    user = User(id=1)
    result = render_template('user.html', user=user)
    assert 0 == result.count('gallery/show/')
