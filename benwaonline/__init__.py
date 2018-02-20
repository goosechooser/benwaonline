import logging
import sys
from flask import Flask, g, url_for, request, flash, redirect, jsonify
from flask_login import LoginManager
from flask_uploads import patch_request_class, configure_uploads

from benwaonline.assets import assets
from benwaonline.oauth import oauth
from benwaonline.entities import User
from benwaonline.front import front
from benwaonline.tags import tags
from benwaonline.gallery import gallery, images
from benwaonline.userinfo import userinfo
from benwaonline.auth import authbp
from benwaonline.gateways import RequestFactory

from benwaonline.config import app_config

FILE_SIZE_LIMIT = 10 * 1024 * 1024
login_manager = LoginManager()

def setup_logger_handlers(loggers):
    fh = logging.FileHandler(__name__ +'_debug.log')
    fh.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    fh.setLevel(logging.DEBUG)
    for logger in loggers:
        logger.addHandler(fh)

    return

def create_app(config_name=None):
    """Returns the Flask app."""
    app = Flask(__name__, template_folder='templates')
    setup_logger_handlers([app.logger, logging.getLogger('gunicorn.error')])
    app.jinja_env.line_statement_prefix = '%'
    app.config.from_object(app_config[config_name])

    assets.init_app(app)
    oauth.init_app(app)
    login_manager.init_app(app)
    rf = RequestFactory()

    @login_manager.user_loader
    def load_user(user_id):
        if user_id:
            r = rf.get(User(), _id=user_id)
            try:
                return User.from_response(r)
            except TypeError:
                pass

        return None

    @login_manager.unauthorized_handler
    def handle_unauthorized():
        return redirect(url_for('authbp.authorize'))

    app.register_blueprint(front)
    app.register_blueprint(gallery)
    app.register_blueprint(authbp)
    app.register_blueprint(userinfo)
    app.register_blueprint(tags)

    configure_uploads(app, (images,))
    patch_request_class(app, FILE_SIZE_LIMIT)

    return app
