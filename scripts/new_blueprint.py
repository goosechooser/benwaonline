import os
import sys
from pathlib import Path

def make_blueprint(blueprint_name):
    maindir = Path(os.getcwd())
    p = Path(maindir)
    p = p / 'benwaonline'
    bp = p / blueprint_name
    bp.mkdir(exist_ok=True)

    fp = bp / '__init__.py'
    with fp.open(mode='w') as f:
        f.write(new_init(blueprint_name))

    views = bp / 'views.py'
    with views.open(mode='w') as f:
        f.write(new_view(blueprint_name))

    templates = bp / 'templates'
    templates.mkdir()

def new_init(blueprint_name):
    template = """from flask import Blueprint\n
front = Blueprint('{}', __name__, template_folder='templates')\n
from benwaonline.{} import views\n""".format(blueprint_name, blueprint_name)
    return template

def new_view(blueprint_name):
    view = """from flask import Blueprint\n
from benwaonline.{} import {}\n""".format(blueprint_name, blueprint_name)
    return view

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('enter a blueprint name')
        exit(0)

    make_blueprint(sys.argv[1])
    # new_init('tags')
