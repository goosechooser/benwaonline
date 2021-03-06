import os
import uuid
from pathlib import PurePath

import requests
from flask import (current_app, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from benwaonline.gateways import (
    CommentGateway, ImageGateway, PreviewGateway,
    TagGateway, PostGateway
)
from benwaonline import entities
from benwaonline.cache import cache
from benwaonline.auth.views import check_token_expiration
from benwaonline.back import back
from benwaonline.exceptions import BenwaOnlineRequestError
from benwaonline.gallery import gallery
from benwaonline.gallery import forms
from benwaonline.util import make_thumbnail

@gallery.route('/gallery/')
@gallery.route('/gallery/<string:tags>/')
@back.anchor
def show_posts(tags='all'):
    ''' Show all posts that match a given tag filter. Shows all posts by default. '''
    post_fields = {'posts': ['title', 'created_on', 'preview']}
    if tags == 'all':
        posts = cache.get('all_posts')
        if not posts:
            posts = PostGateway().get(include=['preview'], fields=post_fields, page_size=0)
            cache.set('all_posts', posts, timeout=3600)
    else:
        tags = tags.split('+')
        posts = PostGateway().tagged_with(tags, include=['preview'], fields=post_fields, page_size=0)

    posts.sort(key=lambda post: post.created_on, reverse=True)
    tags = all_tags()

    return render_template('gallery.html', posts=posts, tags=tags)

@cache.cached(timeout=3600, key_prefix='all_tags')
def all_tags():
    tag_fields = {'tags': ['name', 'num_posts']}
    tags = TagGateway().get(fields=tag_fields)
    tags.sort(key=lambda tag: tag.num_posts, reverse=True)

    return tags

@gallery.route('/gallery/show/<int:post_id>')
@back.anchor
def show_post(post_id):
    '''Displays a single post.
    Consists of an image, any comments about the image, and the tags of the post/image.

    Args:
        post_id: the unique id of the post
    '''
    post = PostGateway().get_by_id(post_id, include=['tags', 'image', 'user'])
    post.load_comments(include=['user'])
    post.tags.sort(key=lambda tag: tag.num_posts, reverse=True)

    return render_template('show.html', post=post, form=forms.CommentForm())

@gallery.route('/gallery/add', methods=['GET', 'POST'])
@back.anchor
@login_required
@check_token_expiration
def add_post():
    '''Creates a new Post'''
    form = forms.PostForm()
    if not form.validate_on_submit():
        flash('There was an issue with adding the benwa')
        return render_template('image_upload.html', form=form)

    form_image = form.image.data
    f_name, f_ext = split_filename(form_image.filename)

    form_image.filename = scrub_filename(f_ext)

    image = create_image(form_image.filename)
    preview = create_preview(form_image.filename)
    tags = create_tags(form.tags.data)

    title = form.title.data or f_name
    post = PostGateway().new(session['access_token'], title=title, tags=tags, image=image, preview=preview, user=current_user)

    msg = 'New post {} posted'.format(post.id)
    current_app.logger.info(msg)

    save_path = save_image(form_image)
    make_thumbnail(save_path, current_app.config['THUMBS_DIR'])

    cache.delete('all_posts')
    cache.delete('all_tags')

    return redirect(url_for('gallery.show_post', post_id=str(post.id)))

def create_image(fname):
    filepath = '/'.join(['imgs', fname])
    return ImageGateway().new(session['access_token'], filepath=filepath)

def create_preview(fname):
    filepath = '/'.join(['thumbs', fname])
    return PreviewGateway().new(session['access_token'], filepath=filepath)

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

def create_tags(tag_names):
    tags = []
    for name in tag_names:
        tag = TagGateway().get_by_name(name)
        if not tag:
            tag = TagGateway().new(name, session['access_token'])
        tags.append(tag)

    tags.append(entities.Tag(id=1))
    return tags

@gallery.route('/gallery/show/<int:post_id>/comment', methods=['POST'])
@login_required
@check_token_expiration
def add_comment(post_id):
    '''Create a new comment for a post.

    Args:
        post_id: the unique id of the post
    '''
    form = forms.CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        CommentGateway().new(content, post_id, current_user, session['access_token'])
        key = 'user_{}'.format(current_user.user_id)
        cache.delete(key)

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
        key = 'user_{}'.format(current_user.user_id)
        cache.delete(key)
    except BenwaOnlineRequestError:
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
    if request.method == 'POST':
        r = current_user.like_post(post_id, session['access_token'])
    else:
        r = current_user.unlike_post(post_id, session['access_token'])

    return jsonify({'status': r.status_code})
