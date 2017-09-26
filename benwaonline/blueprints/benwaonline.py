from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template, flash, current_app

from flask_login import login_user, logout_user, current_user
from flask_security import login_required
from passlib.hash import bcrypt

from benwaonline.database import db
from benwaonline.models import user_datastore, User
from benwaonline.forms import RegistrationForm
from benwaonline.oauth import twitter, login_manager
from benwaonline.misc import random_username

bp = Blueprint('benwaonline', __name__)

@bp.route('/')
def under_construction():
    # return redirect(url_for('gallery.show_posts'))
    return redirect(url_for('benwaonline.test'))

@twitter.tokengetter
def get_twitter_token():
     if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']

@bp.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# @bp.route('/login')
# def login():
#     return render_template('user_login.html')

# @bp.route('/login/auth', methods=['GET', 'POST'])
@bp.route('/login/auth')
def auth():
    if g.user.is_authenticated:
        return redirect('gallery.show_posts')
    callback_url = url_for('benwaonline.oauthorize', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)

@bp.route('/logout')
@login_required
def logout():
    print("i visitinged")
    logout_user()
    return redirect(url_for('benwaonline.test'))

@bp.route('/test')
def test():
    if current_user.is_authenticated:
        return str(current_user.username) + str(current_user.user_id)
    else:
        return "not logged in " + str(current_user.is_authenticated)

@bp.route('/oauthorize')
def oauthorize():
    resp = twitter.authorized_response()
    if not resp:
        flash(u'You denied the request to sign in.')
        return redirect(url_for('gallery.show_posts'))

    session['twitter_oauth'] = resp

    user_id = resp['user_id']
    user = User.query.filter_by(user_id=user_id).first()

    if user:
        login_user(user)
        next = request.args.get('next')
        flash('You were signed in as %s' % user.username)
        return redirect(url_for('benwaonline.test'))
    else:
        session['user_id'] = user_id
        session['token'] = bcrypt.hash(resp['oauth_token'])
        session['secret'] = bcrypt.hash(resp['oauth_token_secret'])
        return redirect(url_for('benwaonline.signup'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = ''.join([form.adj.data, form.benwa.data, form.pos.data])
        name_exists = User.query.filter(User.username == username).all()
        if name_exists:
            flash('Username %s already in use' % username)
            return redirect(url_for('benwaonline.signup'))

        user = user_datastore.create_user(user_id=session['user_id'], username=username,\
                oauth_token_hash=session['token'], oauth_secret_hash=session['secret'])
        db.session.commit()

        login_user(user)
        next = request.args.get('next')

        flash('You were signed in as %s' % user.username)
        return redirect(url_for('benwaonline.test'))

    return render_template('signup.html', form=form)
