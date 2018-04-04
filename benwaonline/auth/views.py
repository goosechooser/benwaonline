import os
import json
from functools import wraps

from jose import jwt

from flask import(
    request, session, redirect, url_for,
    render_template, flash, g, jsonify, current_app
)

from flask_login import login_user, logout_user, current_user
from flask_oauthlib.client import OAuthException
from requests.exceptions import HTTPError

from benwaonline.exceptions import BenwaOnlineError, BenwaOnlineRequestError
from benwaonline.back import back
from benwaonline.oauth import benwa, TokenAuth
from benwaonline.entities import User
from benwaonline import query
from benwaonline.auth import authbp
from benwaonline.auth.forms import RegistrationForm
from benwaonline.auth.core import verify_token, get_jwks, refresh_token_request
from benwaonline import gateways as rf

from benwaonline.config import app_config
cfg = app_config[os.getenv('FLASK_CONFIG')]

@authbp.before_request
def before_request():
    g.user = current_user

@authbp.route('/authorize-info', methods=['GET'])
def authorize_info():
    with authbp.open_resource('templates/login_faq.json', mode='r') as f:
        security_faq = json.loads(f.read())
    return render_template('login.html', entries=security_faq['entries'])

@authbp.route('/authorize', methods=['GET'])
def authorize():
    callback_url = cfg.CALLBACK_URL + url_for('authbp.authorize_callback', next=request.args.get('next'))
    return benwa.authorize(callback=callback_url)

@authbp.route('/authorize/callback')
def authorize_callback():
    '''Handles the authorization response

    Returns:
        a redirection to the previous page, if the user logs in
        otherwise directs them to a signup page
    '''

    save_callback_url()
    resp = handle_authorize_response()

    if not resp:
        return redirect(url_for('authbp.authorize_info'))

    # Obtain tokens and keys to validate signatures
    jwks = get_jwks()
    try:
        payload = verify_token(resp['access_token'])
    except BenwaOnlineError as err:
        msg = 'Error occured during token verification: {}'.format(err)
        current_app.logger.debug(msg)
    else:
        session['access_token'] = resp['access_token']
        session['refresh_token'] = resp['refresh_token']

    user = User(user_id=payload['sub'])
    q = query.Query(query.EntityCriteria('eq', user))
    r = rf.filter(user, q)
    users = User.from_response(r, many=True)

    try:
        user = users[0]
    except IndexError:
        msg = 'Not a single user has signed up ;('
        current_app.logger.info(msg)
        return redirect(url_for('authbp.signup'))

    login_user(user)
    msg = 'User {}: logged in'.format(user.id)
    current_app.logger.info(msg)

    return back.redirect()

def handle_authorize_response():
    """Handles the authorize response from our oauth provider (not twitter's)

    Breaks down into 3 cases:
    * The user didn't receive an authorization response from benwa.online (because they declined twitter's)
    * An issue occured during the token request
    * Everything went ok

    Returns:
        resp: the authorization response if everything went ok, None if it didn't.
    """
    try:
        resp = benwa.authorized_response()
    except OAuthException as err:
        msg = 'OAuthException occured during token request {} {}'.format(err.message, err.data)
        current_app.logger.debug(msg)
        raise BenwaOnlineRequestError(title=err.message, detail=err.data)

    return resp

def save_callback_url():
    """ Manually saves the callback url in session.

    This is supposed to be done by flask-oauthlib, but its not being saved between the 'benwa.authorize' call
    and the 'benwa.authorized_response' call
    """
    callback_url = cfg.CALLBACK_URL + url_for('authbp.authorize_callback', next=request.args.get('next'))
    session['benwaonline_oauthredir'] = callback_url

@authbp.route('/authorize/logout')
def logout():
    try:
        msg = 'User: {} logged out'.format(current_user.id)
    except AttributeError:
        msg = 'Anonymous user logged out'
    current_app.logger.info(msg)
    session.clear()
    logout_user()
    return redirect(url_for('gallery.show_posts'))

@authbp.route('/authorize/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = ' '.join([form.adjective.data, form.benwa.data, form.noun.data])

        if check_username_exists(username):
            flash('Username [%s] already in use, please select another' % username)
            return redirect(url_for('authbp.signup'))

        try:
            auth = TokenAuth(session['access_token'])
        except KeyError as err:
            current_app.logger.debug(err)
            return render_template('signup.html', form=form)

        r = rf.post(User(username=username), auth)

        user = User.from_response(r)
        login_user(user)

        flash('You were signed in as %s' % user.username)
        msg = 'User {}: logged in'.format(user.id)
        current_app.logger.info(msg)
        return back.redirect()

    return render_template('signup.html', form=form)

def check_username_exists(username):
    """Checks if username is already in use. Alerts user if so and returns them to the signup page."""
    user = User(username=username)
    q = query.Query(query.EntityCriteria('eq', user))
    r = rf.filter(user, q)
    users = User.from_response(r, many=True)

    try:
        user = users[0]
    except IndexError:
        return False
    else:
        return True

def check_token_expiration(api_method):
    @wraps(api_method)
    def check_token(*args, **kwargs):
        try:
            verify_token(session['access_token'])
        except jwt.ExpiredSignatureError as err:
            resp = refresh_token_request(benwa, session['refresh_token'])
            try:
                session['access_token'] = resp['access_token']
                session['refresh_token'] = resp['refresh_token']
            except KeyError:
                msg = 'Received error {}'.format(resp['error'])
                current_app.logger.debug(msg)

        return api_method(*args, **kwargs)
    return check_token
