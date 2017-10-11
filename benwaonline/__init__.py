import os
from flask import Flask, g, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_admin import Admin, helpers
from flask_security import Security
from flask_uploads import patch_request_class, configure_uploads

from config import app_config

from benwaonline.database import db
from benwaonline.oauth import oauth
# from benwaonline.admin import setup_adminviews
from benwaonline.models import user_datastore, User
from benwaonline.front import front
from benwaonline.gallery import gallery, images
from benwaonline.user import user
from benwaonline.auth import auth

FILE_SIZE_LIMIT = 10 * 1024 * 1024

security = Security()

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(app_config[config])

    app.config.from_envvar('BENWAONLINE_SETTINGS')
    app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
    db.init_app(app)
    migrate = Migrate(app, db)
    oauth.init_app(app)

    security_ctx = security.init_app(app, user_datastore)
    # @security_ctx.context_processor
    # def security_context_processor():
    #     return dict(
    #         admin_base_template=admin.base_template,
    #         admin_view=admin.index_view,
    #         h=helpers,
    #         get_url=url_for
    # )
    app.login_manager.login_view = 'auth.oauthorize'
    @app.login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.login_manager.unauthorized_handler
    def handle_unauthorized():
        return redirect(url_for('auth.oauthorize'))

    # admin = Admin(app, name='benwaonline', template_mode='bootstrap3')
    # setup_adminviews(admin, db)

    register_cli(app)
    register_teardowns(app)
    app.register_blueprint(front)
    app.register_blueprint(gallery)
    app.register_blueprint(auth)
    app.register_blueprint(user)

    configure_uploads(app, (images,))
    patch_request_class(app, FILE_SIZE_LIMIT)

    return app

def register_cli(app):
    @app.cli.command('initdb')
    def initdb_command():
        """Creates the database tables."""
        init_db()
        print('Initialized the database.')

def init_db():
    import benwaonline.models
    db.create_all()

def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        """Closes the database again at the end of the request."""
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()
