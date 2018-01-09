import os

from urllib.parse import urlencode

from jose import jwt

from flask import(
    request, session, redirect, url_for,
    render_template, flash, g, jsonify
)

from flask_login import login_user, logout_user, current_user, login_required
from flask_oauthlib.client import OAuthException
from flask_restless.views.base import error_response

from benwaonline.exceptions import BenwaOnlineException, BenwaOnlineRequestException
from benwaonline.back import back
from benwaonline.oauth import benwa, TokenAuth
from benwaonline.entities import User
from benwaonline.auth import authbp
from benwaonline.auth.forms import RegistrationForm
from benwaonline.gateways import RequestFactory

from benwaonline.util import verify_token, get_jwks

from config import app_config
cfg = app_config[os.getenv('FLASK_CONFIG')]

rf = RequestFactory()

@authbp.errorhandler(BenwaOnlineException)
def handle_error(error):
    return error_response(error.status, detail=error.detail)

@authbp.before_request
def before_request():
    g.user = current_user

@authbp.route('/authorize', methods=['GET'])
def authorize():
    callback_url = 'http://127.0.0.1:5000' + url_for('authbp.authorize_callback', next=request.args.get('next'))
    return benwa.authorize(callback=callback_url)

@authbp.route('/authorize/callback')
def authorize_callback():
    '''Handles the authorization response

    Returns:
        a redirection to the previous page, if the user logs in
        otherwise directs them to a signup page
    '''
    # For a reason I can't figure out, flask session is being sketchy
    # flask-oauthlib stores the redirect uri for the client in the session
    # but its not being saved between the 'benwa.authorize' call
    # and the 'benwa.authorized_response' call
    # so we set it manually
    session['benwaonline_oauthredir'] = request.base_url

    try:
        resp = benwa.authorized_response()
    except OAuthException as err:
        raise BenwaOnlineRequestException(title=err.message, detail=err.data)

    if resp is None:
        raise BenwaOnlineException('Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ))

    # Obtain tokens and keys to validate signatures
    jwks = get_jwks()

    try:
        payload = verify_token(resp['access_token'], jwks)
    except jwt.JWTError as err:
        print('Decoding access token', err)
    else:
        session['access_payload'] = payload
        session['access_token'] = resp['access_token']

    user_id = session['access_payload']['sub']
    user_filter = [{'name':'user_id', 'op': 'eq', 'val': user_id}]
    r = rf.filter(User(), user_filter, single=True)
    user = User.from_response(r)

    if user:
        login_user(user)
        return back.redirect()

    return redirect(url_for('authbp.signup'))

@authbp.route('/authorize/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('gallery.show_posts'))

# Needs auth required decorator?
@authbp.route('/authorize/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = ' '.join([form.adjective.data, 'Benwa', form.noun.data])
        user_filter = [{'name':'username', 'op': 'eq', 'val': username}]
        r = rf.filter(User(), user_filter, single=True)
        user = User.from_response(r)

        if user:
            flash('Username [%s] already in use, please select another' % username)
            return render_template('signup.html', form=form)

        try:
            auth = TokenAuth(session['access_token'], 'Bearer')
        except KeyError as err:
            flash('There was an error!')
            return render_template('signup.html', form=form)

        r = rf.post(User(username=username), auth)
        user = User.from_response(r)
        login_user(user)
        flash('You were signed in as %s' % user.username)
        return back.redirect()

    return render_template('signup.html', form=form)
