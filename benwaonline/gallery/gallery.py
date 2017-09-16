import random
from datetime import datetime
from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template

from benwaonline import forms
from benwaonline.database import db
from benwaonline.models import Post, Tag, Comment

gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static/', static_url_path='/static/')

NUM = ['420', '69']
CONNECT = ['xXx', '_', '']
ADJ = ['lover', 'liker', 'hater']

@gallery.context_processor
def inject_guestbook_info():
    username = random.choice(CONNECT).join(['benwa', random.choice(ADJ), random.choice(NUM)])

    return {'name' : username}

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
def add_comment(post_id):
    form = forms.Comment(request.form)

    if form.validate():
        post = Post.query.get(post_id)
        comment = Comment(poster_name=form.name.data, content=form.content.data,\
                created=datetime.utcnow(), post=post)

        db.session.add(comment)
        db.session.commit()

    return redirect(url_for('gallery.show_post', post_id=post.id))

# #https://e621.net/post/show/1330331/
# @gallery.route('/gallery/<string:tags>/<int:page>/', methods=['GET', 'POST'])
# def rotating(page=1, tags='all'):
#     if tags == 'all':
#         posts_q = Post.query
#     else:
#         posts_q = Post.query.filter(Post.tags.any(name=tags))

#     posts = posts_q.paginate(page, 1, False)

#     return render_template('rotating.html', posts=posts, tags=tags)
