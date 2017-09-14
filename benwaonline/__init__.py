import os
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import find_modules, import_string

from benwaonline.guestbook.guestbook import guestbook
from benwaonline.gallery.gallery import gallery
from benwaonline.database import db

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
    app.register_blueprint(guestbook)
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
    from benwaonline.models import BenwaPicture, Benwa, Pool
    tag = 'benwas'
    folder = os.path.join(current_app.static_folder, tag, 'imgs')
    print(folder)
    benwas = [f for f in os.listdir(folder)]
    pool = Pool(name=tag)
    db.session.add(pool)

    for benwa in benwas:
        benwaModel = Benwa(name=benwa, owner=pool)
        db.session.add(benwaModel)
        filepath = '/'.join([tag, 'imgs', benwa])
        thumb = '/'.join([tag, 'thumbs', benwa])
        print(filepath)
        print(thumb)
        pic = BenwaPicture(filename=filepath, thumbnail=thumb, date_posted=datetime.utcnow(), views=0, owner=benwaModel)
        db.session.add(pic)

    db.session.commit()

def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        """Closes the database again at the end of the request."""
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()
