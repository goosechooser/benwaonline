import json
import os
import uuid
from pathlib import PurePath

import requests
from flask import (current_app, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required
from requests.exceptions import HTTPError
from werkzeug.utils import secure_filename

from benwaonline import gateways as rf
from benwaonline import entities
from benwaonline.auth.views import check_token_expiration
from benwaonline.back import back
from benwaonline.config import app_config
from benwaonline.exceptions import BenwaOnlineRequestError
from benwaonline.gallery import gallery
from benwaonline.gallery.forms import CommentForm, PostForm
from benwaonline.oauth import TokenAuth
from benwaonline.util import make_thumbnail

cfg = app_config[os.getenv('FLASK_CONFIG')]

@gallery.errorhandler(requests.exceptions.ConnectionError)
def handle_error(e):
    '''Error handler.'''
    error = 'There was an issue connecting to the api service'
    return render_template('error.html', error=error)

@gallery.before_request
def before_request():
    # These means that a GET to /users is gonna happen every request
    # How the f is this gonna impact performance??
    g.user = current_user


@gallery.route('/gallery/')
@gallery.route('/gallery/<string:tags>/')
@back.anchor
def show_posts(tags='all'):
    # Filtering by tags should be moved else where?
    ''' Show all posts that match a given tag filter. Shows all posts by default. '''
    if tags == 'all':
        r = rf.get(entities.Post(), include=['preview'], page_opts={'size': 100})
    else:
        filters = tagname_filter(tags)
        r = rf.filter(entities.Post(), filters, include=['preview'], page_opts={'size': 100})

    posts = entities.Post.from_response(r, many=True)
    posts.sort(key=lambda post: post.id, reverse=True)
    r = rf.get(entities.Tag())
    tags = entities.Tag.from_response(r, many=True)
    tags.sort(key=lambda tag: tag.num_posts, reverse=True)
    return render_template('gallery.html', posts=posts, tags=tags)

def tagname_filter(tags):
    '''Returns a list containing the filter for tags by name

    Args:
        tags (str): A string separated by the '+' character.

    Returns:
        a list containing filters.
    '''
    split_tags = tags.split('+')
    filters = [
        {
            'name': 'tags',
            'op': 'any',
            'val': {
                'name': 'name',
                'op': 'eq',
                'val': tag
            }
        }
        for tag in split_tags]
    filters = {'or': filters}
    return [filters]

@gallery.route('/gallery/show/<int:post_id>')
@back.anchor
def show_post(post_id):
    '''Displays a single post.
    Consists of an image, any comments about the image, and the tags of the post/image.

    Args:
        post_id: the unique id of the post
    '''
    r = rf.get_instance(entities.Post(id=post_id), include=['tags', 'image', 'user'])
    try:
        r.raise_for_status()
    except HTTPError:
        for error in r.json()['errors']:
            raise BenwaOnlineRequestError(error)

    post = entities.Post.from_response(r)

    if any(post.comments):
        r = rf.get_resource(post, entities.Comment(), include=['user'])
        post.comments = entities.Comment.from_response(r, many=True)

    try:
        post.tags.sort(key=lambda tag: tag['num_posts'], reverse=True)
    except KeyError:
        pass
    return render_template('show.html', post=post, form=CommentForm())

@gallery.route('/gallery/add', methods=['GET', 'POST'])
@back.anchor
@login_required
@check_token_expiration
def add_post():
    '''Creates a new Post'''
    form = PostForm()
    if not form.validate_on_submit():
        flash('There was an issue with adding the benwa')
        return render_template('image_upload.html', form=form)

    auth = TokenAuth(session['access_token'])

    f = form.image.data
    pure = PurePath(secure_filename(f.filename))
    filename = pure.stem
    ext = pure.suffix
    fname = ''.join([str(uuid.uuid4().hex), ext])
    save_to = os.path.join(current_app.config['UPLOADED_BENWA_DIR'], fname)
    f.save(save_to)

    make_thumbnail(save_to, current_app.config['THUMBS_DIR'])
    fpath = '/'.join(['thumbs', fname])
    r = rf.post(entities.Preview(filepath=fpath), auth)
    preview = entities.Preview.from_response(r)

    fpath = '/'.join(['imgs', fname])
    r = rf.post(entities.Image(filepath=fpath), auth)
    image = entities.Image.from_response(r)

    if form.tags.data:
        tags = [get_or_create_tag(tag, auth) for tag in form.tags.data if tag]
        tags.append(entities.Tag(id=1))
    else:
        tags = [entities.Tag(id=1)]

    title = form.title.data or filename
    r = rf.post(entities.Post(title=title, tags=tags), auth, include=['tags'])
    post = entities.Post.from_response(r)

    r = rf.patch(post, preview, auth)
    r = rf.patch(post, image, auth)

    rf.add_to(current_user, post, auth)
    msg = 'New post {} posted'.format(post.id)
    current_app.logger.info(msg)
    return redirect(url_for('gallery.show_post', post_id=str(post.id)))

# Caching would be neat here
def get_or_create_tag(name, auth):
    '''Gets a Tag instance if it exists, creates a new one if it doesn't

    Args:
        name: the tag's name
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Tag instance.
    '''
    _filter = [{'name':'name', 'op': 'eq', 'val': name}]
    msg = 'filter built is {}'.format(_filter)
    current_app.logger.debug(msg)

    r = rf.filter(entities.Tag(), _filter)
    msg = 'Tag filtered returned status code {}'.format(r.status_code)
    current_app.logger.debug(msg)

    if r.json()['meta']['count'] == 0:
        msg = 'Creating new tag {}'.format(name)
        current_app.logger.debug(msg)
        r = rf.post(entities.Tag(name=name), auth)
        tag = entities.Tag.from_response(r)

    else:
        tags = entities.Tag.from_response(r, many=True)
        tag = tags[0]

    return tag

# @gallery.route('/post_id/delete', methods=['POST'])
# @login_required
# def delete_post(post_id):
#     uri = '/'.join([current_app.config['API_URL'], 'users', str(g.user.id), 'posts', str(post_id)])
#     r = requests.get(uri, headers=headers, timeout=5)
#     is_owner = r.status_code != 404

#     if current_user.has_role('admin') or is_owner:
#         uri = '/'.join([current_app.config['API_URL'], 'posts', str(post_id)])
#         r = requests.delete(uri, headers=headers, timeout=5)
#     else:
#         flash('you can\'t delete this post')

#     return back.redirect()

@gallery.route('/gallery/show/<int:post_id>/comment', methods=['POST'])
@login_required
@check_token_expiration
def add_comment(post_id):
    '''Create a new comment for a post.

    Args:
        post_id: the unique id of the post
    '''
    form = CommentForm()
    if form.validate_on_submit():
        auth = TokenAuth(session['access_token'])

        # Create comment
        r = rf.post(entities.Comment(content=form.content.data), auth)
        comment = entities.Comment.from_response(r)

        # Update relationships
        # Need to consider what to do if these requests fail for whatever reason
        rf.add_to(current_user, comment, auth)
        rf.add_to(entities.Post(id=post_id), comment, auth)

    return redirect(url_for('gallery.show_post', post_id=post_id))

# Note to self can clean this up to be:
# @gallery.route('/gallery/comment/<int:comment_id>', methods=['DELETE'])
@gallery.route('/gallery/comment/<int:comment_id>/delete', methods=['GET'])
@login_required
@check_token_expiration
def delete_comment(comment_id):
    '''Delete a comment.

    Args:
        comment_id: the unique id of the comment
    '''
    auth = TokenAuth(session['access_token'])
    try:
        rf.delete(entities.Comment(id=comment_id), auth)
    except requests.exceptions.HTTPError:
        flash('you can\'t delete this comment')

    return back.redirect()


@gallery.route('/gallery/show/<int:post_id>/like', methods=['POST', 'DELETE'])
@login_required
@check_token_expiration
def like_post(post_id):
    '''Like or unlike a post.

    Args:
        post_id: the unique id of the post
    '''
    auth = TokenAuth(session['access_token'])
    like = entities.Like(id=post_id)

    if request.method == 'POST':
        r = rf.add_to(current_user, like, auth)
    else:
        r = rf.delete_from(current_user, like, auth)

    return jsonify({'status': r.status_code})
