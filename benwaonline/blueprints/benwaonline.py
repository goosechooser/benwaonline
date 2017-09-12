from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template, flash, current_app

bp = Blueprint('benwaonline', __name__)


@bp.route('/')
def under_construction():
    return render_template('index.html')
