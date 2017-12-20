import os

from urllib.parse import urlencode

from jose import jwt

from flask import request, session, redirect, url_for, render_template, flash, g

from flask_login import login_user, logout_user, current_user, login_required
from flask_oauthlib.client import OAuthException
from flask_restless.views.base import error_response

from benwaonline.exceptions import BenwaOnlineException, BenwaOnlineRequestException
from benwaonline.back import back
from benwaonline.oauth import auth0, TokenAuth
from benwaonline.entities import User
from benwaonline.auth import authbp
from benwaonline.auth.forms import RegistrationForm
from benwaonline.gateways import RequestFactory

from benwaonline.util import verify_token, get_jwks

from config import app_config
cfg = app_config[os.getenv('FLASK_CONFIG')]

rf = RequestFactory()

# STEPS of AUTH0 FLOW
# 1 - web app initiates flow, redirects browser to '/authorize' for authentication
# 2 - Auth0 authenticates the user
# 3 - Auth0 redirects user back to the web app ('redirect_uri' - specified in '/authorize' request)
# with authorization code in the querystring ('code')
# 4 - web app sends the code to Auth0 to exchange for an access_token (using the '/oauth/token' endpoint)
# the web app authenticates with Auth0 using 'client_id' and 'client_secret'
# 5 - Auth0 authenticates the web app, validates 'code' and responds with token
# response of form {'access_token': jwt, 'token_type': 'Bearer'}
# 6 - Web app then uses 'access_token' to call the API for the user

@authbp.errorhandler(BenwaOnlineException)
def handle_error(error):
    return error_response(error.status, detail=error.detail)

@authbp.before_request
def before_request():
    g.user = current_user

# Rewrite
# @authbp.route('/auth/login')
# def oauthorize():
#     callback_uri = request.url_root[:-1] + url_for('authbp.login_callback')

#     return auth0.authorize(callback=callback_uri)

@authbp.route('/auth/login/callback')
def login_callback():
    '''Handles the authorization response

    Returns:
        a redirection to the previous page, if the user logs in
        otherwise directs them to a signup page
    '''
    try:
        # Rewrite
        # resp = auth0.authorized_response()
        pass
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
        # rewrite
        # payload = verify_token(resp['id_token'], jwks, audience=auth0.consumer_key)
        pass
    except (jwt.JWTError, KeyError) as err:
        print('In auth', err)
    else:
        session['id_payload'] = payload
        session['profile'] = {
            'user_id': payload['sub'].split('|')[1],
            'picture': payload.get('picture', None)
        }

    try:
        payload = verify_token(resp['access_token'], jwks)
    except jwt.JWTError as err:
        print('Decoding access token', err)
    else:
        session['access_payload'] = payload
        session['access_token'] = resp['access_token']

    user_id = session['profile']['user_id']
    user_filter = [{'name':'user_id', 'op': 'eq', 'val': user_id}]
    r = rf.filter(User(), user_filter, single=True)
    user = User.from_response(r)

    if user:
        login_user(user)
        return back.redirect()

    return redirect(url_for('authbp.signup'))

# Rewrite
# @authbp.route('/auth/logout')
# @login_required
# def logout():
#     '''Logs the user out

#     Returns:
#         a redirect to the logout handler
#     '''
#     callback_uri = request.url_root[:-1] + url_for('authbp.logout_callback')
#     params = {'returnTo': callback_uri, 'client_id': auth0.consumer_key}
#     return redirect(auth0.base_url + 'v2/logout?' + urlencode(params))

@authbp.route('/auth/logout/callback')
def logout_callback():
    session.clear()
    logout_user()
    return redirect(url_for('gallery.show_posts'))

# Needs auth required decorator
@authbp.route('/auth/signup', methods=['GET', 'POST'])
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
