from datetime import datetime
import random
import sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template, flash, current_app

from benwaonline import forms
from benwaonline import util

bp = Blueprint('benwaonline', __name__)

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
        db.row_factory = sqlite3.Row

    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@bp.route('/')
def under_construction():
    return render_template('under_construction.html')

@bp.route('/benwa')
def benwa():
    pic = util.random_benwa('static/benwas')
    return render_template('benwa.html', filename=pic)

@bp.route('/guestbook')
def show_guestbook():
    entries = query_db('select date, name, text from guestbook order by id desc')
    return render_template('show_guestbook.html', entries=entries)

@bp.context_processor
def inject_guestbook_info():
    numb = ['420', '69']
    joiner = ['xXx', '_', '']
    adj = ['lover', 'liker', 'hater']
    username = random.choice(joiner).join(['benwa', random.choice(adj), random.choice(numb)])

    return {'name' : username}

@bp.route('/guestbook/add', methods=['POST'])
def add_guestbook_entry():
    now = datetime.utcnow().strftime('%d/%m/%Y')
    form = forms.GuestbookEntry(request.form)

    if form.validate():
        db = get_db()
        db.execute('insert into guestbook (name, date, text) values (?, ?, ?)',
                [form.name.data, now, form.comment.data])
        db.commit()
        flash('New entry posted')

    return redirect(url_for('benwaonline.show_guestbook'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You logged in')
            return redirect(url_for('benwaonline.show_guestbook'))

    return render_template('login.html', error=error)

@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You logged out')
    return redirect(url_for('benwaonline.show_guestbook'))