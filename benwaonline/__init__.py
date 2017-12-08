import requests
from marshmallow.exceptions import ValidationError

from flask import Flask, g, url_for, request, flash, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import patch_request_class, configure_uploads

# from benwaonline.database import db
from benwaonline.oauth import oauth
from benwaonline.front import front
from benwaonline.gallery import gallery, images
from benwaonline.userinfo import userinfo
from benwaonline.auth import authbp

from config import app_config
from benwaonlineapi.schemas import UserSchema

FILE_SIZE_LIMIT = 10 * 1024 * 1024

login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask('benwaonline')
    app.config.from_object(app_config[config_name])
    app.config.from_envvar('BENWAONLINE_SETTINGS')

    oauth.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id:
            uri = app.config['API_URL'] + '/users/' + str(user_id)
            r = requests.get(uri, headers={'Accept': 'application/vnd.api+json'}, timeout=5)
            try:
                return UserSchema().load(r.json()).data
            except ValidationError:
                pass

        return None

    # @login_manager.unauthorized_handler
    # def handle_unauthorized():
    #     return redirect(url_for('auth.oauthorize'))

    app.register_blueprint(front)
    app.register_blueprint(gallery)
    app.register_blueprint(authbp)
    app.register_blueprint(userinfo)

    configure_uploads(app, (images,))
    patch_request_class(app, FILE_SIZE_LIMIT)

    return app
