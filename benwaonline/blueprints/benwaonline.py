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
    # return redirect(url_for('gallery.display_posts'))
    return redirect(url_for('benwaonline.test'))

@twitter.tokengetter
def get_twitter_token():
    if 'user' in session:
        user = session['twitter_oauth']
        return user.oauth_token_hash, user.oauth_secret_hash

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# @bp.route('/login')
# def login():
#     return render_template('user_login.html')

# @bp.route('/login/auth', methods=['GET', 'POST'])
@bp.route('/login/auth')
def auth():
    callback_url = url_for('benwaonline.oauthorized', next=request.args.get('next'))
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

@bp.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if not resp:
        flash(u'You denied the request to sign in.')
        return redirect(url_for('gallery.display_posts'))

    user, new = get_or_create_user(resp)
    if new:
        return redirect(url_for('benwaonline.signup'))
    else:
        login_user(user)
        next = request.args.get('next')

        flash('You were signed in as %s' % user.username)
        return redirect(url_for('benwaonline.test'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = ''.join([form.adj.data, form.benwa.data, form.pos.data])
        instance = user_datastore.create_user(user_id=g.session['user_id'], username=username,\
            oauth_token_hash=g.session['token'], oauth_secret_hash=g.session['secret'])
        db.session.commit()

        login_user(instance)
        next = request.args.get('next')

        flash('You were signed in as %s' % username)
        return redirect(url_for('benwaonline.test'))

    return render_template('signup.html', form=form)

def get_or_create_user(response):
    uid = response['user_id']
    instance = User.query.filter_by(user_id=uid).first()

    if instance:
        return instance, False
    else:
        g.session = {}
        g.session['user_id'] = uid
        g.session['token'] = bcrypt.hash(response['oauth_token'])
        g.session['secret'] = bcrypt.hash(response['oauth_token_secret'])

        return None, True
