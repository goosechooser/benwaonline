'''This module contains the views for displaying information about users'''
import os
from flask import render_template, redirect, url_for

from benwaonline.userinfo import userinfo
from benwaonline.gateways import RequestFactory
from benwaonline.entities import User, Post, Comment
from config import app_config

cfg = app_config[os.getenv('FLASK_CONFIG')]
rf = RequestFactory()

@userinfo.route('/users/')
def show_users():
    '''Shows all the current existing users'''
    r = rf.get(User())
    users = User.from_response(r, many=True)
    return render_template('users.html', users=users)

@userinfo.route('/users/<int:user_id>/')
def show_user(user_id):
    '''Displays relevant info for a single user, like comments and posts.

    Args:
        user_id: the user's id
    '''
    r = rf.get(User(), _id=user_id, include=['comments', 'posts', 'posts.preview'])
    user = User.from_response(r)

    if not user:
        return redirect(url_for('userinfo.show_users'))

    r = rf.get_resource(user, Post(), include=['preview'])
    user.posts = Post.from_response(r, many=True)
    return render_template('user.html', user=user)

@userinfo.route('/users/<int:user_id>/comments')
def show_comments(user_id):
    '''Displays all existing comments made by a user.

    Args:
        user_id: the users id
    '''
    r = rf.get_resource(User(id=user_id), Comment(), include=['user'])
    comments = Comment.from_response(r, many=True)
    return render_template('user_comments.html', comments=comments)
