from datetime import datetime
from flask import Blueprint, request, redirect, url_for, render_template
from flask_security import login_required

from benwaonline import forms
from benwaonline.database import db
from benwaonline.models import Post, Tag, Comment

gallery = Blueprint('gallery', __name__, template_folder='templates')

@gallery.route('/gallery/')
@gallery.route('/gallery/<string:tags>/')
def display_posts(tags='all'):
    if tags == 'all':
        posts = Post.query.all()
    else:
        split = tags.split(' ')
        posts = []
        for s in split:
            results = Post.query.filter(Post.tags.any(name=s))
            posts.extend(results)

    tags = Tag.query.all()

    return render_template('gallery.html', posts=posts, tags=tags)

@gallery.route('/gallery/show/<int:post_id>')
def show_post(post_id):
    post = Post.query.get(post_id)

    return render_template('show.html', post=post)

@gallery.route('/gallery/show/<int:post_id>/previous')
def show_previous_post(post_id):
    post = Post.query.order_by(Post.id.desc()).filter(Post.id < post_id).first()
    if post:
        return redirect(url_for('gallery.show_post', post_id=post.id))

    return redirect(request.referrer)

@gallery.route('/gallery/show/<int:post_id>/next')
def show_next_post(post_id):
    post = Post.query.order_by(Post.id.asc()).filter(Post.id > post_id).first()
    if post:
        return redirect(url_for('gallery.show_post', post_id=post.id))

    return redirect(request.referrer)

# Need to make this more generic
@gallery.route('/gallery/show/<int:post_id>/add', methods=['POST'])
@login_required
def add_comment(post_id):
    form = forms.Comment(request.form)

    if form.validate():
        post = Post.query.get(post_id)
        comment = Comment(poster_name=form.name.data, content=form.content.data,\
                created=datetime.utcnow(), post=post)

        db.session.add(comment)
        db.session.commit()

    return redirect(url_for('gallery.show_post', post_id=post.id))
