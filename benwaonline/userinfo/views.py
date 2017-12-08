import requests
from marshmallow import pprint
from flask import render_template, current_app

from benwaonline.userinfo import userinfo
from benwaonlineapi.schemas import UserSchema

headers = {'Accept': 'application/vnd.api+json'}
post_headers = {'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'}

@userinfo.route('/users/')
def show_users():
    uri = '/'.join([current_app.config['API_URL'], 'users'])
    r = requests.get(uri, headers=headers, timeout=5)
    user_data = r.json()['data']
    users = [_attributes(user) for user in user_data]

    return render_template('users.html', users=users)

def _attributes(user):
    attrs = user['attributes']
    attrs['id'] = user['id']
    attrs['comment_count'] = len(user['relationships']['comments']['data'])

    return attrs

@userinfo.route('/users/<int:user_id>/')
def show_user(user_id):
    uri = '/'.join([current_app.config['API_URL'], 'users', str(user_id)])
    response = requests.get(uri, headers=headers, timeout=5)
    user = UserSchema().load(response.json())
    return render_template('user.html', user=user.data)


