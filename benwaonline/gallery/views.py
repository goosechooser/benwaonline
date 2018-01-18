import os
import json
import uuid

import requests

from flask import (
    redirect, url_for, render_template,
    flash, g, current_app, session
)
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

# from scripts import thumb

from benwaonline.util import make_thumbnail
from benwaonline.oauth import TokenAuth
from benwaonline.auth.views import check_token_expiration
from benwaonline.back import back
from benwaonline.gallery import gallery
from benwaonline import gateways
from benwaonline.gallery.forms import CommentForm, PostForm

from benwaonline import entities
from benwaonline.config import app_config

cfg = app_config[os.getenv('FLASK_CONFIG')]

rf = gateways.RequestFactory()

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
        r = rf.get(entities.Post(), include=['preview'])
    else:
        filters = make_filter('tags', tags)
        r = rf.filter(entities.Post(), filters, include=['preview'])

    posts = entities.Post.from_response(r, many=True)
    r = rf.get(entities.Tag())
    tags = entities.Tag.from_response(r, many=True)
    return render_template('gallery.html', posts=posts, tags=tags)

def make_filter(attribute, value):
    '''Creates a filter.

    Refactor this.

    Returns:
        a list containing the filter.
    '''
    name_filter = {'name': 'name', 'op': 'like', 'val': value}
    attr_filter = {'name': attribute, 'op': 'any', 'val': name_filter}
    return [attr_filter]

@gallery.route('/gallery/show/<int:post_id>')
@back.anchor
def show_post(post_id):
    '''Displays a single post.
    Consists of an image, any comments about the image, and the tags of the post/image.

    Args:
        post_id: the unique id of the post
    '''
    r = rf.get(entities.Post(), _id=post_id, include=['tags', 'image'])
    post = entities.Post.from_response(r)

    if post:
        r = rf.get_resource(post, entities.Comment(), include=['user'])
        post.comments = entities.Comment.from_response(r, many=True)
        return render_template('show.html', post=post, form=CommentForm())

    return redirect(url_for('gallery.show_posts'))

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

    auth = TokenAuth(session['access_token'], 'Bearer')

    f = form.image.data
    filename, ext = secure_filename(f.filename).split('.')
    fname = '.'.join([str(uuid.uuid4().hex), ext])
    save_to = os.path.join(current_app.config['UPLOADED_BENWA_DIR'], fname)
    f.save(save_to)

    make_thumbnail(save_to, current_app.config['THUMBS_DIR'])
    fpath = '/'.join(['thumbs', fname])
    r = rf.post(entities.Preview(filepath=fpath), auth)
    preview = entities.Preview.from_response(r)

    fpath = '/'.join(['imgs', fname])
    r = rf.post(entities.Image(filepath=fpath), auth)
    image = entities.Image.from_response(r)

    title = form.title.data or filename
    r = rf.post(entities.Post(title=title), auth)
    post = entities.Post.from_response(r)

    r = rf.patch(post, preview, auth)
    r = rf.patch(post, image, auth)

    if form.tags.data:
        tags = [get_or_create_tag(tag, auth) for tag in form.tags.data if tag]
        tags.append(entities.Tag(id=1))
    else:
        tags = [entities.Tag(id=1)]

    rf.patch_many(post, tags, auth)
    rf.add_to(current_user, post, auth)
    current_app.logger.info('New post', str(post.id), 'posted')
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
    r = rf.filter(entities.Tag(), _filter, single=True)
    if r.status_code != 200:
        r = rf.post(entities.Tag(name=name), auth)

    return entities.Tag.from_response(r)

# @gallery.route('/gallery/post_id/delete', methods=['POST'])
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

@gallery.route('/gallery/show/<int:post_id>/comment/add', methods=['POST'])
@login_required
@check_token_expiration
def add_comment(post_id):
    '''Create a new comment for a post.

    Args:
        post_id: the unique id of the post
    '''
    form = CommentForm()
    if form.validate_on_submit():
        auth = TokenAuth(session['access_token'], 'Bearer')

        # Create comment
        r = rf.post(entities.Comment(content=form.content.data), auth)
        comment = entities.Comment.from_response(r)

        # Update relationships
        # Need to consider what to do if these requests fail for whatever reason
        rf.add_to(current_user, comment, auth)
        rf.add_to(entities.Post(id=post_id), comment, auth)

    return redirect(url_for('gallery.show_post', post_id=post_id))

@gallery.route('/gallery/comment/<int:comment_id>/delete', methods=['GET'])
@login_required
@check_token_expiration
def delete_comment(comment_id):
    '''Delete a comment.

    Args:
        comment_id: the unique id of the comment
    '''
    auth = TokenAuth(session['access_token'], 'Bearer')
    try:
        rf.delete(entities.Comment(id=comment_id), auth)
    except requests.exceptions.HTTPError:
        flash('you can\'t delete this comment')

    return back.redirect()
