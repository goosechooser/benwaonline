'''This module contains the views for displaying information about users'''
import os
from flask import render_template, redirect, url_for
from requests.exceptions import HTTPError

from benwaonline.exceptions import BenwaOnlineRequestError
from benwaonline.userinfo import userinfo
from benwaonline.gateways import UserGateway
from benwaonline.entities import User, Tag, Post
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
    user.load_posts(include=['preview'], page_size='3', sort=['-created_on'])
    user.load_likes(include=['preview'], page_size='3')

    return render_template('user.html', user=user)

@userinfo.route('/users/<int:user_id>/comments')
def show_comments(user_id):
    '''Displays all existing comments made by a user.

    Args:
        user_id: the users id
    '''
    user = User(id=user_id)
    user.load_comments(include=['post.preview', 'user'], fields={'users': ['username']}, page_size=0)

    return render_template('comments.html', comments=user.comments)

@userinfo.route('/users/<int:user_id>/likes')
def show_likes(user_id):
    '''Displays all existing likes made by a user.

    Args:
        user_id: the users id
    '''
    user = User(id=user_id)
    user.load_likes(include=['preview', 'tags'], page_size=0)
    tags = combine_tags(user.likes)

    return render_template('user_posts.html', posts=user.likes, tags=tags)

@userinfo.route('/users/<int:user_id>/posts')
def show_posts(user_id):
    '''Displays all existing likes made by a user.

    Args:
        user_id: the users id
    '''
    user = User(id=user_id)
    user.load_posts(include=['preview', 'tags'], page_size=0)
    tags = combine_tags(user.posts)
    return render_template('user_posts.html', posts=user.posts, tags=tags)

def combine_tags(posts):
    '''Combines lists of tags without adding duplicates.

    Returns:
        a list of dicts representing Tags.
    '''
    tags = list({tag for post in posts for tag in post.tags})
    try:
        tags.sort(key=lambda tag: tag.num_posts, reverse=True)
    except KeyError:
        pass

    return tags

def memo(entry, list_):
    if entry not in list_:
        list_.append(entry)
        return True

    return False