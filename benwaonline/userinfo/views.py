'''This module contains the views for displaying information about users'''
import os
from flask import render_template, redirect, url_for

from benwaonline.userinfo import userinfo
from benwaonline import gateways as rf
from benwaonline.entities import User, Post, Comment, Like, Tag
from benwaonline.config import app_config

cfg = app_config[os.getenv('FLASK_CONFIG')]

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
    r = rf.get_instance(User(id=user_id))
    user = User.from_response(r)

    r = rf.get_resource(user, Post(), include=['preview'], page_opts={'size': 3})
    user.posts = Post.from_response(r, many=True)

    r = rf.get_resource(user, Like(), include=['preview'], page_opts={'size': 3})
    user.likes = Post.from_response(r, many=True)

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


@userinfo.route('/users/<int:user_id>/likes')
def show_likes(user_id):
    '''Displays all existing likes made by a user.

    Args:
        user_id: the users id
    '''
    r = rf.get_resource(User(id=user_id), Like(), include=['preview', 'tags'], page_opts={'size': 0})
    likes = Post.from_response(r, many=True)
    tags = combine_tags(likes)
    try:
        tags.sort(key=lambda tag: tag['num_posts'], reverse=True)
    except KeyError:
        pass

    return render_template('user_posts.html', posts=likes, tags=tags)

@userinfo.route('/users/<int:user_id>/posts')
def show_posts(user_id):
    '''Displays all existing likes made by a user.

    Args:
        user_id: the users id
    '''
    r = rf.get_resource(User(id=user_id), Post(), include=['preview', 'tags'],  page_opts={'size': 0})
    posts = Post.from_response(r, many=True)
    tags = combine_tags(posts)
    try:
        tags.sort(key=lambda tag: tag['num_posts'], reverse=True)
    except KeyError:
        pass

    return render_template('user_posts.html', posts=posts, tags=tags)

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
    return tags
