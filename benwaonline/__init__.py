from flask import Flask, g, url_for, request, flash, redirect, jsonify
from flask_login import LoginManager
from flask_uploads import patch_request_class, configure_uploads

from benwaonline.oauth import oauth
from benwaonline.entities import User
from benwaonline.front import front
from benwaonline.gallery import gallery, images
from benwaonline.userinfo import userinfo
from benwaonline.auth import authbp
from benwaonline.gateways import RequestFactory

from benwaonline.config import app_config

FILE_SIZE_LIMIT = 10 * 1024 * 1024
login_manager = LoginManager()

def create_app(config_name=None):
    """Returns the Flask app."""
    app = Flask(__name__)
    app.jinja_env.line_statement_prefix = '%'
    app.config.from_object(app_config[config_name])

    oauth.init_app(app)
    login_manager.init_app(app)
    rf = RequestFactory()

    @login_manager.user_loader
    def load_user(user_id):
        if user_id:
            r = rf.get(User(), _id=user_id)
            return User.from_response(r)

        return None

    @login_manager.unauthorized_handler
    def handle_unauthorized():
        return redirect(url_for('authbp.authorize'))

    app.register_blueprint(front)
    app.register_blueprint(gallery)
    app.register_blueprint(authbp)
    app.register_blueprint(userinfo)

    configure_uploads(app, (images,))
    patch_request_class(app, FILE_SIZE_LIMIT)

    return app
