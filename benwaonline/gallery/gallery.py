from datetime import datetime
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_security import login_required, current_user

from benwaonline import forms
from benwaonline.database import db
from benwaonline.models import Post, Tag, Comment

gallery = Blueprint('gallery', __name__, template_folder='templates')

@gallery.route('/gallery/')
@gallery.route('/gallery/<string:tags>/')
def show_posts(tags='all'):
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

@gallery.route('/gallery/show/')
def show_post_redirect():
    return redirect(url_for('gallery.show_posts'))

@gallery.route('/gallery/show/<int:post_id>')
def show_post(post_id):
    post = Post.query.paginate(post_id, 1, False)
    if post.items:
        return render_template('show.html', post=post)
    else:
        flash('That Benwa doesn\'t exist yet')
        return redirect(url_for('gallery.show_posts'))

# Need to make this more generic
@gallery.route('/gallery/show/<int:post_id>/add', methods=['POST'])
@login_required
def add_comment(post_id):
    form = forms.Comment(request.form)
    print(form.validate())
    if form.validate():
        post = Post.query.get(post_id)
        comment = Comment(content=form.content.data,\
                created=datetime.utcnow())
        db.session.add(comment)

        post.comments.append(comment)
        current_user.comments.append(comment)
        db.session.commit()

    return redirect(url_for('gallery.show_post', post_id=post.id))
