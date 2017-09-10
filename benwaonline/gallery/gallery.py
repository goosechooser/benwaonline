import random
from datetime import datetime
from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template

from benwaonline import forms
from benwaonline.database import db
from benwaonline.models import BenwaPicture, Benwa, GuestbookEntry

gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static', static_url_path='/static/gallery')

NUM = ['420', '69']
CONNECT = ['xXx', '_', '']
ADJ = ['lover', 'liker', 'hater']

@gallery.context_processor
def inject_guestbook_info():
    username = random.choice(CONNECT).join(['benwa', random.choice(ADJ), random.choice(NUM)])

    return {'name' : username}

@gallery.route('/gallery/')
def display_benwas():
    benwas = Benwa.query.all()
    return render_template('gallery.html', benwas=benwas)

@gallery.route('/gallery/<int:page>/add', methods=['POST'])
def add_comment(page=1):
    print(page)
    form = forms.GuestbookEntry(request.form)
    owner = Benwa.query.filter_by(id=page).first()

    if form.validate():
        entry = GuestbookEntry(name=form.name.data, content=form.content.data,\
                date_posted=datetime.utcnow(), owner=owner)

        db.session.add(entry)
        db.session.commit()

    return redirect(url_for('gallery.rotating', page=owner.id))

@gallery.route('/gallery/<int:page>', methods=['GET', 'POST'])
def rotating(page=1):
    benwas = Benwa.query.paginate(page, 1, False)
    return render_template('rotating.html', benwas=benwas)
