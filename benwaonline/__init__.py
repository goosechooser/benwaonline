import os
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import find_modules, import_string

# from benwaonline.guestbook.guestbook import guestbook
from benwaonline.gallery.gallery import gallery
from benwaonline.database import db
from benwaonline.models import *


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object('config')

    app.config.update(config or {})
    app.config.from_envvar('BENWAONLINE_SETTINGS', silent=True)

    db.init_app(app)
    migrate = Migrate(app, db)

    register_blueprints(app)
    register_cli(app)
    register_teardowns(app)
    # app.register_blueprint(guestbook)
    app.register_blueprint(gallery)

    return app

def register_blueprints(app):
    """
    Register all blueprint modules
    Reference: Armin Ronacher, "Flask for Fun and for Profit" PyBay 2016.
    """
    for name in find_modules('benwaonline.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)

    return None

def register_cli(app):
    @app.cli.command('initdb')
    def initdb_command():
        """Creates the database tables."""
        init_db()
        print('Initialized the database.')

    @app.cli.command('addbenwas')
    def addbenwas_command():
        add_benwas()
        print('Benwas added')

def init_db():
    import benwaonline.models
    db.create_all()

def add_benwas():
    from flask import current_app
    from datetime import datetime
    tag = 'old_benwas'
    folder = os.path.join(current_app.static_folder, tag, 'imgs')
    benwas = [f for f in os.listdir(folder)]
    tag_model = Tag(name=tag, created=datetime.utcnow())
    db.session.add(tag_model)

    for benwa in benwas:
        filepath = '/'.join([tag, 'imgs', benwa])
        img = Image(filepath=filepath, created=datetime.utcnow())
        db.session.add(img)

        thumb = '/'.join([tag, 'thumbs', benwa])
        preview = Preview(filepath=thumb, created=datetime.utcnow())
        db.session.add(preview)

        post = Post(title=benwa, created=datetime.utcnow(), preview=preview, image=img)

        post.tags.append(tag_model)
        db.session.add(post)

    db.session.commit()

def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        """Closes the database again at the end of the request."""
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()
