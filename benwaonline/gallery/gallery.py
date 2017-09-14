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

@gallery.route('/gallery/')
@gallery.route('/gallery/<string:pool>/')
def display_benwas(pool='benwas'):
    pool = Pool.query.filter_by(name=pool).first()
    benwas = pool.members()

    return render_template('gallery.html', benwas=benwas, pool=pool)

@gallery.route('/gallery/<string:pool>/<int:page>/add?<int:benwa_id>', methods=['POST'])
def add_comment(page=1, pool='benwas', benwa_id=0):
    form = forms.GuestbookEntry(request.form)

    if form.validate():
        owner = Benwa.query.filter_by(id=benwa_id).first()
        entry = GuestbookEntry(name=form.name.data, content=form.content.data,\
                date_posted=datetime.utcnow(), owner=owner)

        db.session.add(entry)
        db.session.commit()

    return redirect(url_for('gallery.rotating', page=page, pool=pool))

@gallery.route('/gallery/<string:pool>/<int:page>', methods=['GET', 'POST'])
def rotating(page=1, pool='benwas'):
    pool = Pool.query.filter_by(name=pool).first()
    benwas = pool.benwas.paginate(page, 1, False)

    return render_template('rotating.html', benwas=benwas, pool=pool)
