from datetime import datetime
import random
from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template, flash, current_app

from benwaonline.database import db
from benwaonline.models import GuestbookEntry
from benwaonline import forms

guestbook = Blueprint('guestbook', __name__, template_folder='templates', static_folder='static', static_url_path='/static/guestbook')

@guestbook.context_processor
def inject_guestbook_info():
    numb = ['420', '69']
    joiner = ['xXx', '_', '']
    adj = ['lover', 'liker', 'hater']
    username = random.choice(joiner).join(['benwa', random.choice(adj), random.choice(numb)])

    return {'name' : username}

@guestbook.route('/guestbook')
def show_guestbook():
    # entries = query_db('select date, name, text from guestbook order by id desc')
    # with current_app.app_context():
    entries = GuestbookEntry.query.all()
    return render_template('guestbook.html', entries=reversed(entries))

@guestbook.route('/guestbook/add', methods=['POST'])
def add_guestbook_entry():
    form = forms.GuestbookEntry(request.form)
    print (form.name.data, form.content.data)
    if form.validate():
        entry = GuestbookEntry(name=form.name.data, content=form.content.data,\
                date_posted=datetime.utcnow())

        db.session.add(entry)
        db.session.commit()
        flash('New entry posted')

    return redirect(url_for('guestbook.show_guestbook'))
