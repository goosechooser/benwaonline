import os, random
from datetime import datetime
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

from benwaonline import forms
from benwaonline import util

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'benwaonline.db'),
    DEBUG=True,
    SECRET_KEY='dev key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('BENWAONLINE_SETTINGS', silent=True)

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row

    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def under_construction():
    return render_template('under_construction.html')

@app.route('/benwa')
def benwa():
    pic = util.random_benwa('static/benwas')
    return render_template('benwa.html', filename=pic)

# @app.route('/')
# def show_entries():
#     entries = query_db('select title, text from entries order by id desc')
#     return render_template('show_entries.html', entries=entries)

# @app.route('/add', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_db()
#     db.execute('insert into entries (title, text) values (?, ?)',
#                 [request.form['title'], request.form['text']])
#     db.commit()
#     flash('New entry posted')
#     return redirect(url_for('show_entries'))

@app.route('/guestbook')
def show_guestbook():
    entries = query_db('select date, name, text from guestbook order by id desc')
    return render_template('show_guestbook.html', entries=entries)

@app.context_processor
def inject_guestbook_info():
    numb = ['420', '69']
    joiner = ['xXx', '_', '']
    adj = ['lover', 'liker', 'hater']
    username = random.choice(joiner).join(['benwa', random.choice(adj), random.choice(numb)])

    return {'name' : username}

@app.route('/guestbook/add', methods=['POST'])
def add_guestbook_entry():
    now = datetime.utcnow().strftime('%d/%m/%Y')
    form = forms.GuestbookEntry(request.form)

    if form.validate():
        db = get_db()
        db.execute('insert into guestbook (name, date, text) values (?, ?, ?)',
                [form.name.data, now, form.comment.data])
        db.commit()
        flash('New entry posted')

    return redirect(url_for('show_guestbook'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You logged in')
            return redirect(url_for('show_guestbook'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You logged out')
    return redirect(url_for('show_guestbook'))