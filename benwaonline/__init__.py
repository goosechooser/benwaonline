import logging
import sys
from flask import Flask, g, url_for, request, flash, redirect, jsonify, render_template, make_response, current_app
from flask_login import LoginManager
from flask_uploads import patch_request_class, configure_uploads

from benwaonline.exceptions import BenwaOnlineError, BenwaOnlineRequestError
from benwaonline.cache import cache
from benwaonline.assets import assets
from benwaonline.oauth import oauth
from benwaonline.gateways import UserGateway
from benwaonline.front import front
from benwaonline.tags import tags
from benwaonline.comments import comments
from benwaonline.gallery import gallery, images
from benwaonline.userinfo import userinfo
from benwaonline.auth import authbp

from benwaonline.config import app_config

FILE_SIZE_LIMIT = 10 * 1024 * 1024
login_manager = LoginManager()

def datetimeformat(value, format='%d-%b-%Y'):
    return value.strftime(format)

def create_app(config_name=None):
    """Returns the Flask app."""
    app = Flask(__name__, template_folder='templates')
    setup_logger_handlers(app)
    app.jinja_env.line_statement_prefix = '%'
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.config.from_object(app_config[config_name])

    assets.init_app(app)
    oauth.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id:
            key = 'user_{}'.format(user_id)
            r = cache.get(key)
            if not r:
                r = UserGateway().get_by_user_id(user_id)
                s = cache.set(key, r, timeout=3600)
            return r
        return None

    @login_manager.unauthorized_handler
    def handle_unauthorized():
        return redirect(url_for('authbp.authorize'))

    @app.errorhandler(BenwaOnlineError)
    def handle_error(error):
        args = error.args[0]
        msg = '{} - {}'.format(args['title'], args['source'])
        current_app.logger.debug(msg)
        return render_template('error.html', error=msg)

    @app.errorhandler(BenwaOnlineRequestError)
    def handle_request_error(error):
        msg = 'BenwaOnlineRequestError: {}'.format(error)
        current_app.logger.debug(msg)
        return render_template('request_error.html', error=error)

    register_blueprints(app)

    configure_uploads(app, (images,))
    patch_request_class(app, FILE_SIZE_LIMIT)

    return app

def setup_logger_handlers(app):
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
    ))
    sh.setLevel(logging.DEBUG)
    app.logger.addHandler(sh)

def register_blueprints(app):
    app.register_blueprint(front)
    app.register_blueprint(gallery)
    app.register_blueprint(authbp)
    app.register_blueprint(userinfo)
    app.register_blueprint(tags)
    app.register_blueprint(comments)
