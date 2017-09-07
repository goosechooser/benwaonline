from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app

bp = Blueprint('benwaonline', __name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@bp.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@bp.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry posted')
    return redirect(url_for('benwaonline.show_entries'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.form['username'] != current_app.config['USERNAME']:
        error = 'Invalid username'
    elif request.form['password'] != current_app.config['PASSWORD']:
        error = 'Invalid password'
    else:
        session['logged_in'] = True
        flash('You logged in')
        return redirect(url_for('benwaonline.show_entries'))

    return render_template('login.html', error=error)

@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You logged out')
    return redirect(url_for('benwaonline.show_entries'))

# @app.route("/")
# def index():
#     return render_template('benwa.html' )

# @app.route('/echo/<msg>')
# def echo(msg):
#     return " ".join([msg, 'Benwa'])

# @app.route('/benwa')
# def render_benwa():
#     return send_file(util.random_benwa(app.config['BENWAS']))