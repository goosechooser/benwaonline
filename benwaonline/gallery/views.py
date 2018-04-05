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

from benwaonline.entity_gateway import (
    CommentGateway, ImageGateway, PreviewGateway, TagGateway
)
from benwaonline import gateways as rf
from benwaonline import entities
from benwaonline.query import EntityQuery
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
        split_tags = tags.split('+')
        q = tagname_filter(split_tags)
        r = rf.filter(entities.Post(), q, include=['preview'], page_opts={'size': 100})

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
    tags = [entities.Tag(name=tag) for tag in tags]
    post = entities.Post(tags=tags)
    return EntityQuery(post)
    # return query.Query(query.Or(query.EntityCriteria('any', post)))

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

    form_image = form.image.data
    f_name, f_ext = split_filename(form_image.filename)

    scrubbed = scrub_filename(f_ext)
    form_image.filename = scrubbed

    save_path = save_image(form_image)
    make_thumbnail(save_path, current_app.config['THUMBS_DIR'])

    image = create_image(scrubbed, session['access_token'])
    preview = create_preview(scrubbed, session['access_token'])

    tags = make_tags(form, session['access_token'])

    title = form.title.data or f_name
    post = entities.Post(title=title, tags=tags, image=image, preview=preview, user=current_user)
    r = rf.post(post, auth)
    post = entities.Post.from_response(r)

    msg = 'New post {} posted'.format(post.id)
    current_app.logger.info(msg)
    return redirect(url_for('gallery.show_post', post_id=str(post.id)))

def create_image(fname, auth):
    fpath = '/'.join(['imgs', fname])
    return ImageGateway().new(fpath, auth)

def create_preview(fname, auth):
    fpath = '/'.join(['thumbs', fname])
    return PreviewGateway().new(fpath, auth)

def split_filename(filename):
    pure_file = PurePath(secure_filename(filename))
    return pure_file.stem, pure_file.suffix

def scrub_filename(f_ext):
    return ''.join([str(uuid.uuid4().hex), f_ext])

def save_image(img):
    save_to = os.path.join(current_app.config['UPLOADED_BENWA_DIR'], img.filename)
    msg = 'Saving image to {}'.format(save_to)
    current_app.logger.debug(msg)
    img.save(save_to)
    return save_to

def make_tags(form, auth):
    if form.tags.data:
        tags = [get_or_create_tag(tag, auth) for tag in form.tags.data if tag]
        tags.append(entities.Tag(id=1))
    else:
        tags = [entities.Tag(id=1)]
    return tags

# Caching would be neat here
def get_or_create_tag(name, auth):
    '''Gets a Tag instance if it exists, creates a new one if it doesn't

    Args:
        name: the tag's name
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Tag instance.
    '''
    # tag = entities.Tag(name=name)
    # q = EntityQuery(tag)
    # r = rf.filter(tag, q)
    # tags = entities.Tag.from_response(r, many=True)
    tag = TagGateway().get_by_name(name)
    if not tag:
        tag = TagGateway().new(name, auth)
    return tag
    # # try:
    # #     tag = tags[0]
    # # except IndexError:
    #     r = rf.post(tag, auth)
    #     tag = entities.Tag.from_response(r)

    # return tag

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
        content = form.content.data
        CommentGateway().new(content, post_id, current_user, session['access_token'])

    return redirect(url_for('gallery.show_post', post_id=post_id))

@gallery.route('/gallery/comment/<int:comment_id>/delete', methods=['GET'])
@login_required
@check_token_expiration
def delete_comment(comment_id):
    '''Delete a comment.

    Args:
        comment_id: the unique id of the comment
    '''
    try:
        CommentGateway().delete(comment_id, session['access_token'])
    except BenwaOnlineRequestError as err:
        flash('you can\'t delete this comment')
        print(err)

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
