'''This module contains the views for displaying information about users'''
import os
from flask import render_template, redirect, url_for
from requests.exceptions import HTTPError

from benwaonline.exceptions import BenwaOnlineRequestError
from benwaonline.userinfo import userinfo
from benwaonline.entity_gateways import UserGateway
from benwaonline.entities import User
from benwaonline.config import app_config

cfg = app_config[os.getenv('FLASK_CONFIG')]

@userinfo.errorhandler(BenwaOnlineRequestError)
def handle_error(error):
    return render_template('request_error.html', error=error)

@userinfo.route('/users/')
def show_users():
    '''Shows all the current existing users'''
    users = UserGateway().get()
    return render_template('users.html', users=users)

@userinfo.route('/users/<int:user_id>/')
def show_user(user_id):
    '''Displays relevant info for a single user, like comments and posts.

    Args:
        user_id: the user's id
    '''
    user = UserGateway().get_by_id(user_id, include=['posts', 'likes'])
    user.load_posts(include=['preview'], result_size=3)
    user.load_likes(include=['preview'], result_size=3)

    return render_template('user.html', user=user)

@userinfo.route('/users/<int:user_id>/comments')
def show_comments(user_id):
    '''Displays all existing comments made by a user.

    Args:
        user_id: the users id
    '''
    user = User(id=user_id)
    try:
        user.load_comments(include=['user'])
    except BenwaOnlineRequestError as err:
        return render_template('error.html', error=err)
        
    return render_template('user_comments.html', comments=user.comments)

@userinfo.route('/users/<int:user_id>/likes')
def show_likes(user_id):
    '''Displays all existing likes made by a user.

    Args:
        user_id: the users id
    '''
    user = User(id=user_id)
    user.load_likes(include=['preview', 'tags'], result_size=0)
    tags = combine_tags(user.likes)

    return render_template('user_posts.html', posts=user.likes, tags=tags)

@userinfo.route('/users/<int:user_id>/posts')
def show_posts(user_id):
    '''Displays all existing likes made by a user.

    Args:
        user_id: the users id
    '''
    user = User(id=user_id)
    user.load_posts(include=['preview', 'tags'],  page_opts={'size': 0})
    tags = combine_tags(user.posts)

    return render_template('user_posts.html', posts=user.posts, tags=tags)

def combine_tags(posts):
    '''Combines lists of tags without adding duplicates.

    Returns:
        a list of dicts representing Tags.
    '''
    tags = []
    for post in posts:
        for tag in post.tags:
            if tag not in tags:
                tags.append(tag)

    try:
        tags.sort(key=lambda tag: tag['num_posts'], reverse=True)
    except KeyError:
        pass

    return tags
