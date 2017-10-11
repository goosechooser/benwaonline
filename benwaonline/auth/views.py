from flask import request, session, g, redirect, url_for, \
     render_template, flash

from flask_security import login_required, login_user, logout_user, current_user

from benwaonline.back import back
from benwaonline.database import db
from benwaonline.oauth import twitter
from benwaonline.models import user_datastore, User, Role
from benwaonline.auth import auth
from benwaonline.auth.forms import RegistrationForm

@auth.before_request
def before_request():
    g.user = current_user

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return back.redirect()

# def login():
#     return redirect(url_for('auth.oauthorize'))

@auth.route('/login/auth', methods=["GET", "POST"])
def oauthorize():
    if g.user.is_authenticated:
        return back.redirect()

    if request.method == 'POST':
        callback_url = url_for('auth.oauthorize_callback', next=request.args.get('next'))
        return twitter.authorize(callback=callback_url)

    return render_template('login.html', url=back.url())

@auth.route('/oauthorize')
def oauthorize_callback():
    resp = twitter.authorized_response()
    if not resp:
        flash(u'You denied the request to sign in.')
        return back.redirect()

    user_id = resp['user_id']
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        login_user(user)
        flash('You were signed in as %s' % user.username)
        return back.redirect()

    session['user_id'] = user_id
    session['token'] = resp['oauth_token']
    session['secret'] = resp['oauth_token_secret']
    return redirect(url_for('auth.signup'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if g.user.is_authenticated:
        return back.redirect()

    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        adjective = form.adjective.data
        noun = form.noun.data
        username = ' '.join([adjective, 'Benwa', noun])

        user = create_user(session['user_id'], username, session['token'], session['secret'])

        if not user:
            return render_template('signup.html', form=form)

        login_user(user)

        session.pop('token')
        session.pop('secret')

        flash('You were signed in as %s' % user.username)
        return back.redirect()

    return render_template('signup.html', form=form)

def create_user(user_id, username, token, secret):
    name_exists = User.query.filter_by(username=username).first()
    if name_exists:
        flash('Username [%s] already in use, please select another' % username)
        return None

    user = user_datastore.create_user(user_id=user_id, username=username,
            oauth_token=token, oauth_secret=secret)
    db.session.commit()

    user_datastore.add_role_to_user(user, Role.query.filter_by(name='member').first())
    db.session.commit()

    return user
