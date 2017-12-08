import os
import uuid
import json
from urllib import parse

import requests
from marshmallow import pprint

from flask import redirect, url_for, render_template, flash, g, current_app, session, jsonify
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

from scripts.thumb import make_thumbnail

from benwaonline.oauth import TokenAuth
from benwaonline.back import back
from benwaonline.gallery import gallery
from benwaonline.gallery import base
from benwaonline.gateways import *
from benwaonline.gallery.forms import CommentForm, PostForm

from benwaonlineapi.schemas import PostSchema, ImageSchema, PreviewSchema, CommentSchema, TagSchema, UserSchema
from benwaonlineapi.util import requires_scope
from config import app_config

headers = {'Accept': 'application/vnd.api+json'}
post_headers = {'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'}

cfg = app_config[os.getenv('FLASK_CONFIG')]

postg = PostGateway(cfg.API_URL + '/posts')
pg = PreviewGateway(cfg.API_URL + '/previews')
ig = ImageGateway(cfg.API_URL + '/images')
tg = TagGateway(cfg.API_URL + '/tags')
ug = UserGateway(cfg.API_URL + '/users')
cg = CommentGateway(cfg.API_URL + '/comments')

@gallery.before_request
def before_request():
    g.user = current_user

@gallery.route('/gallery/')
@gallery.route('/gallery/<string:tags>/')
@back.anchor
def show_posts(tags='all'):
    # Filtering by tags should be moved else where?
    ''' Show all posts that match a given tag filter. Shows all posts by default. '''
    if tags == 'all':
        posts = postg.get(include=['preview'])
    else:
        filters = make_filter('tags', tags)
        posts = postg.filter(filters, include=['preview'])

    tags = tg.get()
    return render_template('gallery.html', posts=posts, tags=tags)

def make_filter(attribute, value):
        ''' Returns a '''
        name_filter = {'name': 'name', 'op': 'like', 'val': value}
        attr_filter = {'name': attribute, 'op': 'any', 'val': name_filter}
        return [attr_filter]

@gallery.route('/gallery/show/<int:post_id>')
@back.anchor
def show_post(post_id):
    ''' Display a single post '''
    try:
        post = postg.get(_id=post_id, include=['comments', 'tags', 'image'])
    except requests.exceptions.HTTPError:
        return redirect(url_for('gallery.show_posts'))

    return render_template('show.html', post=post, form=CommentForm())

# Will need to add Role/Permissions to this later
@gallery.route('/gallery/add', methods=['GET', 'POST'])
@back.anchor
@login_required
def add_post():
    '''
    Creates a new Post
    '''
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
    preview = pg.post({'filepath': fpath}, auth)
    preview_patch = PreviewSchema().dumps(preview).data

    fpath = '/'.join(['imgs', fname])
    image = ig.post({'filepath': fpath}, auth)
    image_patch = ImageSchema().dumps(image).data

    title = form.title.data or filename
    post = postg.post({'title': title}, auth)

    postg.patch(post['id'], 'preview', preview_patch, auth)
    postg.patch(post['id'], 'image', image_patch, auth)

    if form.tags.data:
        tags = [get_or_create_tag(tag, auth) for tag in form.tags.data if tag]
        tags.append({'id': '1'})
    else:
        tags = [{'id': '1'}]

    tag_patch = TagSchema(many=True).dumps(tags).data
    postg.patch(post['id'], 'tags', tag_patch, auth)

    post_patch = PostSchema(many=True).dumps([post]).data
    postg.add_to(ug.api_endpoint, g.user.id, 'posts', post_patch, auth)

    return redirect(url_for('gallery.show_post', post_id=str(post['id'])))

# Redis would be neat here
def get_or_create_tag(tag, auth):
    _filter = [{'name':'name', 'op': 'eq', 'val': tag}]
    try:
        return tg.filter(_filter, single=True)
    except requests.exceptions.HTTPError:
        return tg.post({'name': tag}, auth)

@gallery.route('/gallery/post_id/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    uri = '/'.join([current_app.config['API_URL'], 'users', str(g.user.id), 'posts', str(post_id)])
    r = requests.get(uri, headers=headers, timeout=5)
    is_owner = r.status_code != 404

    if current_user.has_role('admin') or is_owner:
        uri = '/'.join([current_app.config['API_URL'], 'posts', str(post_id)])
        r = requests.delete(uri, headers=headers, timeout=5)
    else:
        flash('you can\'t delete this post')

    return back.redirect()

@gallery.route('/gallery/show/<int:post_id>/comment/add', methods=['POST'])
@login_required
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        # Create comment
        auth = TokenAuth(session['access_token'], 'Bearer')
        comment = cg.post({'content': form.content.data}, auth=auth)

        # Update relationships
        comment_patch = CommentSchema(many=True).dumps([comment]).data
        cg.add_to(ug.api_endpoint, str(current_user.id), 'comments', comment_patch, auth)
        cg.add_to(postg.api_endpoint, str(post_id), 'comments', comment_patch, auth)

    return redirect(url_for('gallery.show_post', post_id=post_id))

@gallery.route('/gallery/comment/<int:comment_id>/delete', methods=['GET'])
@login_required
def delete_comment(comment_id):
    uri = '/'.join([current_app.config['API_URL'], 'users', str(g.user.id), 'comments', str(comment_id)])
    r = requests.get(uri, headers=headers, timeout=5)
    is_owner = r.status_code != 404

    # if is_owner or 'delete:other-comments' in scope
    if is_owner or requires_scope('delete:other-comments', session['access_payload']):
        uri = '/'.join([current_app.config['API_URL'], 'comments', str(comment_id)])
        r = requests.delete(uri, headers=headers, timeout=5)
    else:
        flash('you can\'t delete this comment')

    return back.redirect()
