import random
from datetime import datetime
from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template

from benwaonline import forms
from benwaonline.database import db
from benwaonline.models import *

gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static/', static_url_path='/static/')

NUM = ['420', '69']
CONNECT = ['xXx', '_', '']
ADJ = ['lover', 'liker', 'hater']

@gallery.context_processor
def inject_guestbook_info():
    username = random.choice(CONNECT).join(['benwa', random.choice(ADJ), random.choice(NUM)])

    return {'name' : username}

#e621 does /post/
# post/index/<int:page>/
# post/index/<int:page>/<tags>
# def display_posts():
#     posts = Post.query.all()

#     return render_template('gallery.html', posts=posts, tag=None)

def process_post_query(model, tag):
    posts = Post.query.all()
    if tag:
        posts = posts.filter(Post.tags.any(name=tag))
        
    return tag
@gallery.route('/gallery/')
@gallery.route('/gallery/<string:tag>/')
def display_posts(tag=None):
    posts = Post.query.all()
    if tag:
        posts = posts.filter(Post.tags.any(name=tag))
    print(posts)

    return render_template('gallery.html', posts=posts, tag=tag)

@gallery.route('/gallery/<string:tag>/<int:page>/add?<int:post_id>', methods=['POST'])
def add_comment(page=1, tag='benwas', post_id=1):
    form = forms.GuestbookEntry(request.form)

    if form.validate():
        post = Post.query.get(post_id)
        comment = Comment(poster_name=form.name.data, content=form.content.data,\
                created=datetime.utcnow(), post=post)

        db.session.add(comment)
        db.session.commit()

    return redirect(url_for('gallery.rotating', page=page, tag=tag))

#https://e621.net/post/show/1330331/
@gallery.route('/gallery/<string:tag>/<int:page>', methods=['GET', 'POST'])
def rotating(page=1, tag='benwas'):
    posts_q = Post.query.filter(Post.tags.any(name=tag))
    posts = posts_q.paginate(page, 1, False)

    return render_template('rotating.html', posts=posts, tag=tag)
