import json
from functools import wraps

from flask import (current_app, flash, make_response, redirect,
                   render_template, request, session, url_for)
from flask_login import current_user, login_user, logout_user
from flask_oauthlib.client import OAuthException
from jose import jwt

from benwaonline.auth import authbp
from benwaonline.auth.core import get_jwks, refresh_token_request, verify_token
from benwaonline.auth.forms import RegistrationForm
from benwaonline.back import back
from benwaonline.cache import cache
from benwaonline.exceptions import BenwaOnlineError, BenwaOnlineRequestError
from benwaonline.gateways import UserGateway
from benwaonline.oauth import benwa

def check_token_expiration(api_method):
    @wraps(api_method)
    def check_token(*args, **kwargs):
        try:
            verify_token(session['access_token'])
        except jwt.ExpiredSignatureError:
            msg = 'Token expired. Refreshing'
            current_app.logger.debug(msg)
            resp = refresh_token_request(benwa, session['refresh_token'])
            try:
                session['access_token'] = resp['access_token']
                session['refresh_token'] = resp['refresh_token']
            except KeyError:
                msg = 'Received error {}'.format(resp['error'])
                current_app.logger.debug(msg)

        return api_method(*args, **kwargs)
    return check_token

@authbp.errorhandler(BenwaOnlineRequestError)
def handle_request_error(error):
    msg = 'BenwaOnlineRequestError @ auth: {}'.format(error)
    current_app.logger.debug(msg)
    return make_response(render_template('request_error.html', error=error), 200)

@authbp.route('/authorize-info', methods=['GET'])
def authorize_info():
    with authbp.open_resource('templates/login_faq.json', mode='r') as f:
        security_faq = json.loads(f.read())
    return render_template('login.html', entries=security_faq['entries'])

@authbp.route('/authorize', methods=['GET'])
def authorize():
    callback_url = current_app.config['CALLBACK_URL'] + url_for('authbp.authorize_callback', next=request.args.get('next'))
    return benwa.authorize(callback=callback_url)

@authbp.route('/authorize/callback')
def authorize_callback():
    '''Handles the authorization response

    Returns:
        a redirection to the previous page, if the user logs in
        otherwise directs them to a signup page
    '''
    headers = ['{}: {}'.format(k,v) for k, v in request.headers.items()]
    msg = 'received request with\n{}'.format('\n'.join(headers))
    current_app.logger.debug(msg)

    resp = handle_authorize_response()

    if not resp:
        msg = 'Did not receive an authorization response'
        current_app.logger.debug(msg)
        return redirect(url_for('authbp.authorize_info'))

    msg = 'Received authorization response'
    current_app.logger.debug(msg)

    try:
        payload = verify_token(resp['access_token'])
    except BenwaOnlineError as err:
        msg = 'Error occured during token verification: {}'.format(err)
        current_app.logger.debug(msg)
    else:
        session['access_token'] = resp['access_token']
        session['refresh_token'] = resp['refresh_token']

    msg = 'Checking if user has signed up before'
    current_app.logger.debug(msg)

    user = UserGateway().get_by_user_id(payload['sub'])

    if not user:
        msg = 'New user. Redirecting to signup.'
        current_app.logger.debug(msg)
        return redirect(url_for('authbp.signup'))

    cache.set('user_{}'.format(user.user_id), user)
    login_user(user)

    msg = 'User {}: logged in'.format(user.user_id)
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
    save_callback_url()

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
    callback_url = current_app.config['CALLBACK_URL'] + url_for('authbp.authorize_callback', next=request.args.get('next'))
    session['benwaonline_oauthredir'] = callback_url

@authbp.route('/authorize/logout')
def logout():
    try:
        msg = 'User: {} logged out'.format(current_user.id)
        current_app.logger.info(msg)
        cache.delete('user_{}'.format(current_user.id))
    except AttributeError:
        pass

    session.clear()
    logout_user()
    return redirect(url_for('gallery.show_posts'))

@authbp.route('/authorize/signup', methods=['GET', 'POST'])
@check_token_expiration
def signup():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = ' '.join([form.adjective.data, form.benwa.data, form.noun.data])

        if UserGateway().get_by_username(username):
            flash('Username [%s] already in use, please select another' % username)
            return redirect(url_for('authbp.signup'))

        user = UserGateway().new(username, session['access_token'])
        login_user(user)

        flash('You were signed in as %s' % user.username)
        msg = 'User {}: logged in'.format(user.id)
        current_app.logger.info(msg)
        return back.redirect()

    return render_template('signup.html', form=form)
